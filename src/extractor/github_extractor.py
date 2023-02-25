import requests
import json
import pandas as pd
import numpy as np
from src.common import create_session
from src.common import column_to_datetime
from src.common import rename_and_drop_fields
from concurrent.futures import ThreadPoolExecutor, as_completed

pd.options.mode.chained_assignment = None  # default='warn'


class GithubExtractor:
    github_url = ""
    github_user = ""
    github_token = ""
    github_org = ""
    commits = dict()
    mappings = dict()
    certificate_path = ""

    def __init__(self, config, github_token):
        self.github_url = config["GITHUB"]["github_url"]
        self.github_user = config["GITHUB"]["github user"]
        self.github_org = config["GITHUB"]["github_org"]
        self.github_token = github_token
        self.certificate_path = config["COMMON"]["certificat_path"]
        with open("src/mappings/github_mappings.json") as json_file:
            self.mappings = json.load(json_file)

    def create_session(self):
        return create_session(self.github_user, self.github_token)

    def execute_paginated_request(self, endpoint, parameters={"per_page": 100}):
        another_page = True
        url = f"{self.github_url}/{endpoint}"
        results = []
        while another_page:
            with self.create_session() as session:
                r = session.get(url, params=parameters, verify=self.certificate_path)
            json_response = r.json()
            results.extend(json_response)
            if "next" in r.links:  # check if there is another page of organisations
                url = r.links["next "]["url"]
            else:
                another_page = False
        return results

    def extract_team_list(self):
        response = self.execute_paginated_request(f"orgs/{self.github_org}/teams")
        return response

    def transform_team_list(self, response):
        df_teams = pd.json_normalize(response)
        df_teams = df_teams[["name", "id"]]
        team_list = df_teams.to_dict("records")
        return team_list

    def get_team_list(self):
        response = self.extract_team_list()
        team_list = self.transform_team_list(response)
        return team_list

    def extract_team_repos(self, team):
        response = self.execute_paginated_request(
            f"orgs/{self.github_org}/teams/{team}/repos"
        )
        return response

    def get_writer_teams_repos(self, team_list):
        df_team_list = pd.DataFrame(team_list)
        df_team_list = df_team_list[df_team_list["name"].str.contains("Writer")]
        writer_team_list = df_team_list["name"].to_list()
        repos_dict = dict()
        with ThreadPoolExecutor(max_workers=20) as executor:
            threads = []
            for writer_team in writer_team_list:
                print(writer_team)
                threads.append(executor.submit(self.extract_team_repos, writer_team))

        for task in as_completed(threads):
            team_repos = task.result()
            if not team_repos:
                repos_dict[writer_team] = []
                continue
            df_team_repos = pd.json_normalize(team_repos)
            repos_list = df_team_repos["name"].to_list()
            repos_dict[writer_team] = repos_list
        return repos_dict

    def extract_pull_requests(self, team, repo):
        params = {"per _page": 100, "state": "closed"}
        response = self.execute_paginated_request(
            f"repos/{self.github_org}/{repo}/pulls"
        )
        response_dict = {"team": team, "repo": repo, "response": response}
        return response_dict

    def transform_pull_requests(self, response_dict):
        pulls = response_dict["response"]
        df_pulls = pd.jon_normalize(pulls)
        df_pulls = rename_and_drop_fields(self.mappings["pulls"], df_pulls)
        df_pulls["repo"] = response_dict["repo"]
        df_pulls["team"] = response_dict["team"]
        df_pulls = column_to_datetime(df_pulls, "created")
        df_pulls = column_to_datetime(df_pulls, "closed")
        df_pulls = column_to_datetime(df_pulls, "merged")
        return df_pulls

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

    def transform_commits_pulls(self, df_pulls):
        df_commits = df_pulls[["number", "repo"]]
        df_commits.loc[:, ("commit_list")] = df_commits.apply(
            lambda x: self.extract_commits_list_from_pr_number(x["number"], x["repo"]),
            axis=1,
        )
        df_commits = df_commits.explode("commit _list", True)
        df_flattened_commits = pd.json_normalize(df_commits["commit list"])
        df_commits = df_commits.join(df_flattened_commits)
        df_commits = rename_and_drop_fields(self.mappings["commits"], df_commits)
        df_commits - column_to_datetime(df_commits, "commit_date")
        return df_commits

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
