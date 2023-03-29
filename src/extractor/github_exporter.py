import requests
import json
import pandas as pd
from src.extractor.exporter import Exporter
from src.common import common
from concurrent.futures import ThreadPoolExecutor, as_completed

pd.options.mode.chained_assignment = None  # default='warn'


class GithubExporter(Exporter):
    def initialize_data(self, config):
        self.github_url = config["GITHUB"]["github_url"]
        self.github_user = config["GITHUB"]["github_user"]
        self.github_org = config["GITHUB"]["github_org"]
        self.github_repo_list = config["GITHUB"]["github_repo_list"].split(",")
        self.github_token = config["GITHUB"]["github_token"]
        # self.certificate_path = config["COMMON"]["certificat_path"]
        with open("src/extractor/github_mappings.json") as json_file:
            self.mappings = json.load(json_file)
        self.commits = dict()

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        session = requests.Session()
        session.auth = (self.github_user, self.github_token)
        session.headers.update(headers)
        return session

    def execute_paginated_request(
        self, endpoint, parameters={"per_page": 100}
    ):
        another_page = True
        url = f"{self.github_url}/{endpoint}"
        results = []
        while another_page:
            with self.create_session() as session:
                # r = session.get(url, params=parameters, verify=self.certificate_path)
                r = session.get(url, params=parameters, verify=False)
            json_response = r.json()
            results.extend(json_response)
            if (
                "next" in r.links
            ):  # check if there is another page of organisations
                url = r.links["next"]["url"]
            else:
                another_page = False
        return results

    def extract_data(self):
        all_pulls = self.extract_all_pull_requests(self.github_repo_list)
        pr_keys = self.get_pr_repo_number_list(all_pulls)
        all_commits = self.extract_all_commits(pr_keys)
        all_reviews = self.extract_all_reviews(pr_keys)
        return {
            "pulls": all_pulls,
            "commits": all_commits,
            "reviews": all_reviews,
        }

    def extract_all_pull_requests(self, repo_list):
        all_pulls = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo in repo_list:
                threads.append(
                    executor.submit(self.extract_pull_requests, repo)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_pulls.append(response_dict)
        return all_pulls

    def extract_pull_requests(self, repo):
        params = {"per _page": 100, "state": "closed"}
        response = self.execute_paginated_request(
            f"repos/{self.github_org}/{repo}/pulls", params
        )
        response_dict = {"repo": repo, "response": response}
        return response_dict

    def get_pr_repo_number_list(self, pull_list):
        df_all_pulls = pd.DataFrame()
        for pr in pull_list:
            curr_pull = pd.json_normalize(pr["response"])
            curr_pull["repo"] = pr["repo"]
            curr_pull = curr_pull[["repo", "number"]]
            df_all_pulls = pd.concat([df_all_pulls, curr_pull])
        all_pulls_list = list(df_all_pulls.itertuples(index=False, name=None))
        return all_pulls_list

    def extract_all_commits(self, pr_list):
        all_commits = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo, number in pr_list:
                threads.append(
                    executor.submit(self.extract_pr_commits, repo, number)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_commits.append(response_dict)
        return all_commits

    def extract_pr_commits(self, repo, number):
        params = {"per _page": 100}
        response = self.execute_paginated_request(
            f"repos/{self.github_org}/{repo}/pulls/{number}/commits", params
        )
        response_dict = {"repo": repo, "number": number, "response": response}
        return response_dict

    def extract_all_reviews(self, pr_list):
        all_reviews = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for repo, number in pr_list:
                threads.append(
                    executor.submit(self.extract_pr_reviews, repo, number)
                )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    all_reviews.append(response_dict)
        return all_reviews

    def extract_pr_reviews(self, repo, number):
        params = {"per _page": 100}
        response = self.execute_paginated_request(
            f"repos/{self.github_org}/{repo}/pulls/{number}/reviews", params
        )
        response_dict = {"repo": repo, "number": number, "response": response}
        return response_dict

    def adapt_data(self, raw_data):
        all_pulls = raw_data["pulls"]
        df_pulls = self.adapt_pulls(all_pulls)
        all_commits = raw_data["commits"]
        df_commits = self.adapt_commits(all_commits)
        all_reviews = raw_data["reviews"]
        df_reviews = self.adapt_reviews(all_reviews)
        return {
            "df_pulls": df_pulls,
            "df_commits": df_commits,
            "df_reviews": df_reviews,
        }

    def adapt_pulls(self, all_pulls):
        df_pulls = pd.DataFrame()
        for pull in all_pulls:
            df_curr_pull = pd.json_normalize(pull["response"])
            df_curr_pull["repo"] = pull["repo"]
            df_curr_pull = common.df_drop_and_rename_columns(
                df_curr_pull, self.mappings["pulls"]
            )
            df_pulls = pd.concat([df_pulls, df_curr_pull])
        return df_pulls

    def adapt_commits(self, all_commits):
        df_commits = pd.DataFrame()
        for commit in all_commits:
            df_curr_commits = pd.json_normalize(commit["response"])
            df_curr_commits["repo"] = commit["repo"]
            df_curr_commits["number"] = commit["number"]
            df_curr_commits = common.df_drop_and_rename_columns(
                df_curr_commits, self.mappings["commits"]
            )
            df_commits = pd.concat([df_commits, df_curr_commits])
        return df_commits

    def adapt_reviews(self, all_reviews):
        df_reviews = pd.DataFrame()
        for review in all_reviews:
            df_curr_reviews = pd.json_normalize(review["response"])
            df_curr_reviews["repo"] = review["repo"]
            df_curr_reviews["number"] = review["number"]
            df_curr_reviews = common.df_drop_and_rename_columns(
                df_curr_reviews, self.mappings["reviews"]
            )
            df_reviews = pd.concat([df_reviews, df_curr_reviews])
        return df_reviews
