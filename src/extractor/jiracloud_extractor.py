import requests
import math
import csv
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


class JiraCloud:
    def __init__(self, config):
        self.email = config["JIRA_CLOUD"]["jira_user_email"]
        self.token = config["JIRA_CLOUD"]["jira_token"]
        self.jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self.project_key = config["JIRA_CLOUD"]["jira_project_key"]

        self.creation_status = config["JIRA_CLOUD"]["jira_creation_status"]
        self.released_status = config["JIRA_CLOUD"]["jira_released_status"]
        self.closed_statuses = config["JIRA_CLOUD"]["jira_closed_statuses"].split(",")

        self.df_versions = pd.DataFrame()
        self.df_status_changes = pd.DataFrame()

    def get_status_changes(self):
        if (self.df_status_changes.empty):
            changelogs = self.extract_status_changelogs()
            status_changes = self.transform_status_changelogs(changelogs)
            self.df_status_changes = status_changes
        return self.df_status_changes

    def get_release_management(self):
        if (self.df_versions.empty):
            versions = self.extract_versions()
            transformed_versions = self.transform_versions(versions)
            self.df_versions = transformed_versions
        return self.df_versions

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        session = requests.Session()
        session.auth = (self.email, self.token)
        session.headers.update(headers)
        return session

    def execute_project_version_request(self, parameters, is_recursive=True):
        version_url = f"{self.jira_adress}/rest/api/2/project/{self.project_key}/version?"
        parameters_string = f"{parameters}" if parameters else ""

        version_query = f"{version_url}{parameters_string}"

        with self.create_session() as session:
            response = session.get(version_query)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        response_json = response.json()
        issues = response_json["values"]
        total = response_json["total"]
        current_issue = 200

        if not is_recursive:
            return issues
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            print(f"Total releases: {total}")
            while (current_issue < total):
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAT={current_issue}"
                threads.append(executor.submit(self.execute_project_version_request, next_parameters, is_recursive=False))
                current_issue += 200
        for task in as_completed(threads):
            issues.extend(task.results())
        
        return issues

    def execute_jql_request(self, query, fields, parameters, is_recursive=True):
        jira_url = f"{self.jira_adress}/rest/api/2/search?"

        fields_string = f"&fields={fields}" if fields else None
        parameter_string = f"&{parameters}" if parameters else None
        query_string = f"jql={query}"

        with self.create_session() as session:
            response = session.get(f"{jira_url}{query_string}{fields_string}{parameter_string}")
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        
        response_json = response.json()
        issues = response_json["issues"]
        total = response_json["total"]
        current_issue = 200
        if not is_recursive:
            return issues

        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            print(f"Total issues: {total}")
            while (current_issue < total):
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAt={current_issue}"
                threads.append(executor.submit(self.execute_jql_request, query, fields, next_parameters, is_recursive=False))
                current_issue += 200
        for task in as_completed(threads):
            issues.extend(task.result())

        return issues

    def extract_versions(self):
        parameters = "maxResults=200"
        versions = self.execute_project_version_request(parameters)
        return versions

    def transform_versions(self, versions):
        fieldnames_mapping = {
            "name": "name",
            "description": "description",
            "releaseDate": "release_date",
            "startDate": "start_date"
        }
        fields_to_keeps = ["name", "description", "release_date", "start_date"]
        df_versions = pd.json_normalize(versions)
        df_versions = df_versions.rename(columns=fieldnames_mapping)
        df_versions = df_versions[df_versions["released"] == True]
        if ("release_date" in df_versions):
            df_versions["release_date"] = pd.to_datetime(df_versions["release_date"], utc=True, errors="coerce").dt.tz_convert(None)
        else:
            df_versions["release_date"] = None
        if ("start_date" in df_versions):
            df_versions["start_date"] = pd.to_datetime(df_versions["start_date"], utc=True, errors="coerce").dt.tz_convert(None)
        else:
            df_versions["start_date"] = None
        df_versions = self.df_drop_columns(df_versions, fields_to_keeps)

        df_versions["event_type"] = "release_management"
        df_versions["project_key"] = self.project_key
        df_versions["control_date"] = df_versions["release_date"]

        return df_versions

    def extract_status_changelogs(self):
        fields = f"issuetype,status,created,project,parent,fixVersions"
        parameters = f"expand=changelog&maxResults=200"
        query = f"project={self.project_key} AND issuetype in (Story)"

        changelogs = self.execute_jql_request(query, fields, parameters)

        return changelogs

    def transform_status_changelogs(self, changelogs):
        fieldnames_mapping = {
            "key": "key",
            "fields.project.key": "project_key",
            "fields.parent.key": "parent_key",
            "fields.issuetype.name": "issue_type",
            "fromString": "from_status",
            "toString": "to_status",
            "changelog.histories.created": "to_date",
            "name": "version"
        }
        fields_to_keep = ["key", "project_key", "parent_key", "issue_type", "from_status", "to_status", "to_date", "from_date", "version"]

        df_changelogs = pd.json_normalize(changelogs, ["changelog", "histories", "items"], ["key", ["changelog", "histories", "created"]])
        df_changelogs = df_changelogs[df_changelogs["field"] == "status"]
        df_fields = pd.json_normalize(changelogs)
        df_status_changes = df_changelogs.merge(df_fields)

        df_versions = pd.json_normalize(changelogs, ["fields", "fixVersions"], ["key"])
        df_versions = df_versions[["key", "name"]]
        df_versions = df_versions.fillna("no_version")
        df_versions = df_versions.groupby("key", as_index=False).agg({"name": ",".join})
        df_status_changes = df_status_changes.merge(df_versions)

        df_status_changes["changelog.histories.created"] = pd.to_datetime(df_status_changes["changelog.histories.created"], utc=True, errors="coerce").dt.tz_convert(None)
        df_status_changes["fields.created"] = pd.to_datetime(df_status_changes["fields.created"], utc=True, errors="coerce").dt.tz_convert(None)
        df_status_changes["from_date"] = df_status_changes.sort_values(["changelog.histories.created"]).groupby("key")["changelog.histories.created"].shift()
        df_status_changes["from_date"] = df_status_changes["from_date"].fillna(df_status_changes["fields.created"])
        df_status_changes.loc[df_status_changes.sort_values(["changelog.histories.created"]).groupby("key")["fromString"].head(1).index, "fromString"] = self.creation_status
        
        df_status_changes = df_status_changes.rename(columns=fieldnames_mapping)
        df_status_changes = self.df_drop_columns(df_status_changes, fields_to_keep)
        df_status_changes["event_type"] = "status_change"

        df_status_changes = self.add_transition_to_released_status(df_status_changes)
        df_status_changes["control_date"] = df_status_changes["to_date"]
        
        return df_status_changes

    def add_transition_to_released_status(self, df_status_changes):
        df_closed = df_status_changes[df_status_changes["to_status"].isin(self.closed_statuses)]
        df_closed_dedup = df_closed.loc[df_closed.groupby("key")["to_date"].transform("max") == df_closed["to_date"]]

        df_released = pd.DataFrame()
        for row in df_closed_dedup.itertuples():
            versions = row.version.split(",")
            df_version = self.get_release_management()
            dates = df_version[df_version["name"].isin(versions)][["release_date","name"]].dropna()
            if len(dates) != 0:
                min_id = dates["release_date"].idxmin()
                new_row = df_closed_dedup.loc[[row.Index]].copy()
                new_row["from_status"] = new_row["to_status"]
                new_row["from_date"] = new_row["to_date"]
                new_row["to_status"] = self.released_status
                new_row["to_date"] = dates.loc[min_id]["release_date"]
                new_row["release_version"] = dates.loc[min_id]["name"]
                df_released = pd.concat([df_released, new_row])
        df_status_changes = pd.concat([df_status_changes, df_released])
        return df_status_changes

    def df_drop_columns(self, dataframe, columns_to_keep):
        for col in dataframe.columns:
            if col not in columns_to_keep:
                dataframe = dataframe.drop(columns=col)
        return dataframe
