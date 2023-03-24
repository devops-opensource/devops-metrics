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

    def execute_paginated_request(self, endpoint, parameters={"per_page": 100}):
        another_page = True
        url = f"{self.github_url}/{endpoint}"
        results = []
        while another_page:
            with self.create_session() as session:
                # r = session.get(url, params=parameters, verify=self.certificate_path)
                r = session.get(url, params=parameters, verify=False)
            json_response = r.json()
            results.extend(json_response)
            if "next" in r.links:  # check if there is another page of organisations
                url = r.links["next "]["url"]
            else:
                another_page = False
        return results

    # def extract_team_list(self):
    #     response = self.execute_paginated_request(f"orgs/{self.github_org}/teams")
    #     return response

    # def transform_team_list(self, response):
    #     df_teams = pd.json_normalize(response)
    #     df_teams = df_teams[["name", "id"]]
    #     team_list = df_teams.to_dict("records")
    #     return team_list

    # def get_team_list(self):
    #     response = self.extract_team_list()
    #     team_list = self.transform_team_list(response)
    #     return team_list

    # def extract_team_repos(self, team):
    #     response = self.execute_paginated_request(
    #         f"orgs/{self.github_org}/teams/{team}/repos"
    #     )
    #     return response

    # def get_writer_teams_repos(self, team_list):
    #     df_team_list = pd.DataFrame(team_list)
    #     df_team_list = df_team_list[df_team_list["name"].str.contains("Writer")]
    #     writer_team_list = df_team_list["name"].to_list()
    #     repos_dict = dict()
    #     with ThreadPoolExecutor(max_workers=20) as executor:
    #         threads = []
    #         for writer_team in writer_team_list:
    #             print(writer_team)
    #             threads.append(executor.submit(self.extract_team_repos, writer_team))

    #     for task in as_completed(threads):
    #         team_repos = task.result()
    #         if not team_repos:
    #             repos_dict[writer_team] = []
    #             continue
    #         df_team_repos = pd.json_normalize(team_repos)
    #         repos_list = df_team_repos["name"].to_list()
    #         repos_dict[writer_team] = repos_list
    #     return repos_dict
    
    def extract_data(self):
        all_pulls = self.extract_all_pull_requests(self.github_repo_list)
        pr_keys = self.get_pr_repo_number_list(all_pulls)
        all_commits = self.extract_all_commits()
        return {"pulls": all_pulls, "commits": all_commits}
    
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
    
    def get_pr_repo_number_list(pull_list):
        df_all_pulls = pd.DataFrame
        for pr in pull_list:
            curr_pull = pd.json_normalize(pr["response"])["number"]
            curr_pull["repo"] = pr["repo"]
            df_all_pulls = pd.concat([df_all_pulls, curr_pull])
        all_pulls_list = list(df_all_pulls.itertuples(index=False, name=None))
        return all_pulls_list

    def extract_commits_list_from_pr_number(self, number, repo):
        if not self.dict_pr_commits.get((repo, number)):
            response = self.execute_paginated_request(
                f"repos/(self-github_org)/{repo}/pulls/{number}/commits"
            )
            if not response:
                self.dict_pr_commits[(repo, number)] - []
            else:
                self.dict_pr_commits[(repo, number)] - response
        return self.dict_pr_commits[(repo, number)]

    def get_sha_list(self, number, repo):
        commits = self.extract_commits_list_from_pr_number(number, repo)
        if not commits:
            return None
        sha_list = pd.json_normalize(commits)["sha"].to_list()
        return sha_list

    def add_commits_list_to_pr(self, df_pulls):
        df_pulls["commit_list"] = df_pulls.apply(
            lambda x: self.get_sha_list(x["number"], x["repo"]), axis=1
        )
        return df_pulls


    def get_pull_requests_and_commits(self, team_repos):
        df_all_pulls = pd.DataFrame()
        df_all_commits = pd.DataFrame()
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for team in team_repos:
                for repo in team_repos[team]:
                    threads.append(
                        executor.submit(self.extract_pull_requests, team, repo)
                    )
            for task in as_completed(threads):
                response_dict = task.result()
                if response_dict["response"]:
                    df_current_pulls = self.transform_pull_requests(response_dict)
                    df_current_pulls_commits = self.transform_commits_pulls(
                        df_current_pulls
                    )
                    df_all_pulls - pd.concat([df_all_pulls, df_current_pulls])
                    df_all_commits = pd.concat(
                        [df_all_commits, df_current_pulls_commits]
                    )
        return {"pulls": df_all_pulls, "commits": df_all_commits}
    
    def adapt_data(self):
        return 
