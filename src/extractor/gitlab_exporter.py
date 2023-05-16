import requests
import json
import pandas as pd
from src.extractor.exporter import Exporter
from src.common import common
from concurrent.futures import ThreadPoolExecutor, as_completed

pd.options.mode.chained_assignment = None


class GitlabExporter(Exporter):
    def initialize_data(self, config):
        self.gitlab_url = config["GITLAB"]["gitlab_url"]
        self.gitlab_user = config["GITLAB"]["gitlab_user"]
        self.gitlab_org = config["GITLAB"]["gitlab_org"]
        self.gitlab_repo_list = config["GITLAB"]["gitlab_repo_list"].split(",")
        self.gitlab_token = config["GITLAB"]["gitlab_token"]
        with open("src/extractor/gitlab_mappings.json") as json_file:
            self.mappings = json.load(json_file)
        self.commits = dict()

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Private-Token": self.gitlab_token,
        }
        session = requests.Session()
        session.headers.update(headers)
        return session

    def execute_paginated_request(self, endpoint, parameters={}):
        another_page = True
        url = f"{self.gitlab_url}/{endpoint}"
        results = []
        while another_page:
            with self.create_session() as session:
                r = session.get(url, params=parameters, verify=False)
            json_response = r.json()
            if not isinstance(json_response, list):
                json_response = [json_response]
            results.extend(json_response)
            if "next" in r.links:
                url = r.links["next"]["url"]
            else:
                another_page = False
        return results

    def extract_data(self):
        all_merge_requests = self.extract_all_merge_requests(
            self.gitlab_repo_list
        )
        mr_keys = self.get_mr_repo_id_iid_list(all_merge_requests)
        all_commits = self.extract_all_commits(mr_keys)
        all_reviewers = self.extract_all_reviewers(mr_keys)
        all_repo_names = self.extract_all_repo_names(self.gitlab_repo_list)
        return {
            "merge_requests": all_merge_requests,
            "commits": all_commits,
            "reviewers": all_reviewers,
            "repo_names": all_repo_names,
        }

    def extract_all_merge_requests(self, repo_list):
        all_pulls = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo in repo_list:
                threads.append(
                    executor.submit(self.extract_merge_requests, repo)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_pulls.append(response_dict)
        return all_pulls

    def extract_merge_requests(self, repo):
        params = {"per _page": 100, "state": "merged"}
        response = self.execute_paginated_request(
            f"projects/{repo}/merge_requests", params
        )
        response_dict = {"repo": repo, "response": response}
        return response_dict

    def get_mr_repo_id_iid_list(self, merge_request_list):
        df_all_pulls = pd.DataFrame()
        for pr in merge_request_list:
            curr_pull = pd.json_normalize(pr["response"])
            curr_pull["repo"] = pr["repo"]
            curr_pull = curr_pull[["repo", "iid"]]
            df_all_pulls = pd.concat([df_all_pulls, curr_pull])
        all_pulls_list = list(df_all_pulls.itertuples(index=False, name=None))
        return all_pulls_list

    def extract_all_commits(self, mr_list):
        all_commits = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo, iid in mr_list:
                threads.append(
                    executor.submit(self.extract_mr_commits, repo, iid)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_commits.append(response_dict)
        return all_commits

    def extract_mr_commits(self, project_id, merge_request_iid):
        params = {"per_page": 100}
        response = self.execute_paginated_request(
            f"projects/{project_id}/merge_requests/ \
            {merge_request_iid}/commits",
            params,
        )
        response_dict = {
            "repo": project_id,
            "iid": merge_request_iid,
            "response": response,
        }
        return response_dict

    def extract_all_reviewers(self, mr_list):
        all_reviews = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo, iid in mr_list:
                threads.append(
                    executor.submit(self.extract_mr_reviewers, repo, iid)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_reviews.append(response_dict)
        return all_reviews

    def extract_mr_reviewers(self, project_id, merge_request_iid):
        params = {}
        response = self.execute_paginated_request(
            f"projects/{project_id}/merge_requests/{merge_request_iid}/notes",
            params,
        )
        response_dict = {
            "repo": project_id,
            "iid": merge_request_iid,
            "response": response,
        }
        return response_dict

    def extract_all_repo_names(self, repo_list):
        all_repos = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo in repo_list:
                threads.append(executor.submit(self.extract_repo_names, repo))
            for task in as_completed(threads):
                response = task.result()
                if response != []:
                    all_repos.extend(response)
        return all_repos

    def extract_repo_names(self, project_id):
        params = {}
        response = self.execute_paginated_request(
            f"projects/{project_id}", params
        )
        return response

    def adapt_data(self, raw_data):
        repo_name_dict = self.get_repo_names_dict(raw_data["repo_names"])
        all_merge_requests = raw_data["merge_requests"]
        df_merge_requests = self.adapt_merge_requests(
            all_merge_requests, repo_name_dict
        )
        all_commits = raw_data["commits"]
        df_commits = self.adapt_commits(all_commits, repo_name_dict)
        all_reviewers = raw_data["reviewers"]
        df_reviewers = self.adapt_reviewers(all_reviewers, repo_name_dict)
        return {
            "df_pulls": df_merge_requests,
            "df_commits": df_commits,
            "df_reviews": df_reviewers,
        }

    def get_repo_names_dict(self, all_repo_names):
        df_repo_names = pd.json_normalize(all_repo_names)
        df_repo_names = df_repo_names[["id", "name"]]
        repo_dict = df_repo_names.set_index("id").to_dict(orient="index")
        return repo_dict

    def adapt_merge_requests(self, all_merge_requests, repo_name_dict):
        df_merge_requests = pd.DataFrame()
        for merge_request in all_merge_requests:
            df_curr_merge_request = pd.json_normalize(
                merge_request["response"]
            )
            df_curr_merge_request["repo"] = repo_name_dict[
                int(merge_request["repo"])
            ]["name"]
            df_curr_merge_request = common.df_drop_and_rename_columns(
                df_curr_merge_request, self.mappings["merge_requests"]
            )
            df_merge_requests = pd.concat(
                [df_merge_requests, df_curr_merge_request]
            )
        return df_merge_requests

    def adapt_commits(self, all_commits, repo_name_dict):
        df_commits = pd.DataFrame()
        for commit in all_commits:
            df_curr_commits = pd.json_normalize(commit["response"])
            df_curr_commits["repo"] = repo_name_dict[int(commit["repo"])][
                "name"
            ]
            df_curr_commits["iid"] = commit["iid"]
            df_curr_commits = common.df_drop_and_rename_columns(
                df_curr_commits, self.mappings["commits"]
            )
            df_commits = pd.concat([df_commits, df_curr_commits])
        return df_commits

    def adapt_reviewers(self, all_reviewers, repo_name_dict):
        df_reviewers = pd.DataFrame()
        for reviewer in all_reviewers:
            if "error" in reviewer["response"]:
                continue

            df_curr_reviewers = pd.json_normalize(reviewer["response"])
            df_curr_reviewers = df_curr_reviewers.assign(
                repo=repo_name_dict[int(reviewer["repo"])]["name"],
                iid=reviewer["iid"],
            )
            df_reviewers = pd.concat([df_reviewers, df_curr_reviewers])

        df_reviewers = df_reviewers[
            df_reviewers["body"].str.contains("approved")
        ]
        df_reviewers = common.df_drop_and_rename_columns(
            df_reviewers, self.mappings["reviewers"]
        )
        return df_reviewers

    def save_data(self, dataframes, file_prefix):
        file_prefix = f"{file_prefix}_gitlab"
        common.save_dataframes_to_csv(dataframes, file_prefix)
