from __future__ import annotations
from src.extractor import exporter
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import json
import src.common.common as common
from contextlib import closing


class JiracloudExporter(exporter.Exporter):
    """
    The Creator class declare the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    def initialize_data(self, config):
        self._email = config["JIRA_CLOUD"]["jira_user_email"]
        self._token = config["JIRA_CLOUD"]["jira_token"]
        self._jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self._project_keys = config["JIRA_CLOUD"]["jira_project_keys"]

        with open("src/extractor/mappings.json") as json_file:
            mapping = json.load(json_file)
            self._versions_mapping = mapping["versions"]
            self._status_changes_mapping = mapping["status_changes"]

    def extract_data(self):
        project_version_dict = self.extract_project_versions()
        status_changes_dict = self.extract_status_changelogs()
        data_dict = {
            "versions": project_version_dict,
            "status_changes": status_changes_dict,
        }
        return data_dict

    def adapt_data(self, data_dict):
        adapted_dict = dict()
        for key in data_dict:
            if key is "versions":
                adapted_dict["versions"] = self.adapt_versions(
                    data_dict["versions"]
                )
            elif key is "status_changes":
                adapted_dict["status_changes"] = self.adapt_status_changes(
                    data_dict["status_changes"]
                )
        return adapted_dict

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        session = requests.Session()
        session.auth = (self._email, self._token)
        session.headers.update(headers)
        return session

    def execute_project_version_request(
        self, project_key, parameters, is_recursive=True
    ):
        version_url = (
            f"{self._jira_adress}/rest/api/2/project/{project_key}/version?"
        )
        parameters_string = f"{parameters}" if parameters else ""

        version_query = f"{version_url}{parameters_string}"

        with closing(self.create_session()) as session:
            response = session.get(version_query)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        response_json = response.json()
        issues = response_json["values"]
        total = response_json["total"]
        number_of_issue_per_page = response_json["maxResults"]
        current_issue = number_of_issue_per_page

        if not is_recursive:
            return issues

        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            print(f"Total releases: {total}")
            while current_issue < total:
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAt={current_issue}"
                threads.append(
                    executor.submit(
                        self.execute_project_version_request,
                        project_key,
                        next_parameters,
                        is_recursive=False,
                    )
                )
                current_issue += number_of_issue_per_page
        for task in as_completed(threads):
            issues.extend(task.result())

        return issues

    def extract_project_versions(self):
        project_version_dict = dict()
        project_key_list = self._project_keys.split(",")
        for project_key in project_key_list:
            project_version_dict[
                project_key
            ] = self.execute_project_version_request(project_key, "")
        return project_version_dict

    def execute_jql_request(
        self, query, fields, parameters, is_recursive=True
    ):
        jira_url = f"{self._jira_adress}/rest/api/2/search?"

        fields_string = f"&fields={fields}" if fields else None
        parameter_string = f"&{parameters}" if parameters else None
        query_string = f"jql={query}"

        with closing(self.create_session()) as session:
            response = session.get(
                f"{jira_url}{query_string}{fields_string}{parameter_string}"
            )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        response_json = response.json()
        issues = response_json["issues"]
        total = response_json["total"]
        number_of_issue_per_page = response_json["maxResults"]
        current_issue = number_of_issue_per_page
        if not is_recursive:
            return issues

        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            print(f"Total issues: {total}")
            while current_issue < total:
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAt={current_issue}"
                threads.append(
                    executor.submit(
                        self.execute_jql_request,
                        query,
                        fields,
                        next_parameters,
                        is_recursive=False,
                    )
                )
                current_issue += number_of_issue_per_page
        for task in as_completed(threads):
            issues.extend(task.result())

        return issues

    def extract_status_changelogs(self):
        fields = f"issuetype,status,created,project,parent,fixVersions"
        parameters = f"expand=changelog"
        query = f"project IN ({self._project_keys}) AND issuetype in (Story)"

        changelogs = self.execute_jql_request(query, fields, parameters)

        return changelogs

    def adapt_versions(self, versions_dict):
        df_all_projects_versions = pd.DataFrame()
        for project_key in versions_dict:
            df_versions = pd.json_normalize(versions_dict[project_key])
            if df_versions.empty:
                continue
            df_versions = common.df_drop_and_rename_columns(
                df_versions, self._versions_mapping
            )
            df_versions["project_key"] = project_key
            df_all_projects_versions = pd.concat(
                [df_all_projects_versions, df_versions]
            )
        return df_all_projects_versions

    def adapt_status_changes(self, status_changes):
        df_changelogs = pd.json_normalize(
            status_changes,
            ["changelog", "histories", "items"],
            ["key", ["changelog", "histories", "created"]],
        )
        df_changelogs = df_changelogs[df_changelogs["field"] == "status"]
        df_fields = pd.json_normalize(status_changes)
        df_status_changes = df_changelogs.merge(df_fields)

        df_versions = pd.json_normalize(
            status_changes, ["fields", "fixVersions"], ["key"]
        )
        df_versions = df_versions[["key", "name"]]
        df_versions = df_versions.fillna("no_version")
        df_versions = df_versions.groupby("key", as_index=False).agg(
            {"name": ",".join}
        )
        df_status_changes = df_status_changes.merge(df_versions)

        df_status_changes = common.df_drop_and_rename_columns(
            df_status_changes, self._status_changes_mapping
        )
        return df_status_changes

    
