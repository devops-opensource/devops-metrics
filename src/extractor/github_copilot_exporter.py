import requests
import json
import pandas as pd
import sys
import os
from src.extractor.exporter import Exporter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

pd.options.mode.chained_assignment = None  # default='warn'


class GithubCopilotExporter(Exporter):
    def initialize_data(self, config):
        self.github_url = config["GITHUB"]["github_url"]
        self.github_org = config["GITHUB"]["github_org"]
        self.github_token = config["GITHUB"]["github_token"]

        # For future reference if the need for mappings arises
        #with open("src/extractor/github_mappings.json") as json_file:
        #    self.mappings = json.load(json_file)
        #self.commits = dict()

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization" : "Bearer " + self.github_token
        }
        session = requests.Session()
        #session.auth = (self.github_user, self.github_token)
        session.headers.update(headers)
        return session

    def execute_paginated_request(self, endpoint, parameters={"per_page": 100}):
        """
        Méthode générique pour appeler n'importe quel endpoint GitHub
        avec pagination, en combinant self.github_url et 'endpoint'.
        """
        another_page = True
        url = f"{self.github_url}/{endpoint}"
        results = []
        while another_page:
            with self.create_session() as session:
                r = session.get(url, params=parameters, verify=False)
            json_response = r.json()
            results.extend(json_response)

            if "next" in r.links:
                url = r.links["next"]["url"]
            else:
                another_page = False
        return results

    def execute_simple_request(self, endpoint):
        """
        Méthode simple, sans pagination, pour appeler n'importe quel endpoint GitHub.
        """
        url = f"{self.github_url}/{endpoint}"
        with self.create_session() as session:
            r = session.get(url)
        return r.json()

    def extract_data(self):
        teams = self.extract_teams()
        metrics_per_team = self.extract_metrics_per_team(teams)

        daily_active_users = self.extract_daily_active_users()
        # average active users calculated using raw daily_active_users data in the transformer
        new_seats_added, inactive_users = self.extract_seats_information()
        return {
            "daily_active_users": daily_active_users,
            "new_seats_added": new_seats_added,
            "inactive_users": inactive_users,
            "metrics_per_team": metrics_per_team
        }
    
    def extract_metrics_per_team(self, teams):
        """
        Retrieve Copilot metrics for each team and store them in a dict
        keyed by the team's slug.
        """
        team_metrics = {}
        for team in teams:
            endpoint = f"orgs/{self.github_org}/teams/{team['slug']}/copilot/metrics"
            metrics = self.execute_paginated_request(endpoint)
            team_metrics[team['slug']] = metrics
        return team_metrics
    
    def extract_metrics_global(self):
        """
        Retrieve Copilot metrics at the organization (global) level.
        This is a high-level summary of metrics for the entire org.
        """
        endpoint = f"orgs/{self.github_org}/copilot/metrics"
        # Reuse our paginated request just as we do for teams
        global_metrics = self.execute_paginated_request(endpoint)

        return global_metrics
    
    def extract_daily_active_users(self):
        # Note: there is a discrepency between the active users returned by /metrics and /usage
        # Note 2: active users is typically more elevated than the alternative field "engaged_users" since it tracks people who may have logged in but not used the tool
        endpoint = f"{self.github_org}/copilot/metrics"
        all_metrics = self.execute_paginated_request(endpoint)
        daily_active_users = {}
        for metric in all_metrics:
            daily_active_users[metric['date']] = metric['total_active_users']
        return daily_active_users
    
    def extract_seats_information(self):
        endpoint = f"{self.github_org}/copilot/billing"
        seats_information = self.execute_simple_request(endpoint)
        seats_information_breakdown = seats_information['seat_breakdown']
        return (
            {'added_this_cycle': seats_information_breakdown['added_this_cycle']},
            {'inactive_this_cycle': seats_information_breakdown['inactive_this_cycle']}
        )

    def extract_teams(self):
        endpoint = f"orgs/{self.github_org}/teams"
        teams = self.execute_paginated_request(endpoint)
        return teams

    def adapt_data(self, raw_data):
        daily_active_users = raw_data["daily_active_users"]
        df_daily_active_users = self.adapt_daily_active_users(daily_active_users)
        
        
        added_seats, inactive_seats = raw_data["new_seats_added"], raw_data["inactive_users"]
        df_seats = self.adapt_seats_information(added_seats, inactive_seats)
    
        return {
            "df_daily_active_users": df_daily_active_users,
            "df_seats": df_seats
        }
    
    def adapt_daily_active_users(self, daily_active_users):
        df = pd.DataFrame.from_dict(daily_active_users, orient='index', columns=['active_users'])
        
        df.index = pd.to_datetime(df.index)
        df.index.name = 'date'
        df = df.reset_index()
        
        df['date'] = pd.to_datetime(df['date'])
        df['active_users'] = df['active_users'].astype(int)
        
        return df

    def adapt_seats_information(self, added_seats, inactive_seats):
        df = pd.DataFrame({
            'added_seats': [added_seats['added_this_cycle']],
            'inactive_seats': [inactive_seats['inactive_this_cycle']]
        })
        return df
    
    def adapt_metrics_chat_global(self, metrics_global, team: str = None):
        """
        Adapt the global Copilot metrics data into a DataFrame with the specified format.

        Parameters:
            metrics_global (list): List of metrics data from extract_metrics_global.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - editor_name
                - model_name
                - total_engaged_users
                - total_chat
                - total_chat_insertion_events
                - total_chat_copy_events
        """
        records = []
        for metric in metrics_global:
            date = metric.get('date')
            copilot_ide_chat = metric.get('copilot_ide_chat', {})
            editors = copilot_ide_chat.get('editors', [])
            for editor in editors:
                editor_name = editor.get('name')
                models = editor.get('models', [])
                for model in models:
                    record = {
                        'team': team,
                        'date': date,
                        'editor_name': editor_name,
                        'model_name': model.get('name'),
                        'total_engaged_users': model.get('total_engaged_users'),
                        'total_chat': model.get('total_chats', 0),
                        'total_chat_insertion_events': model.get('total_chat_insertion_events', 0),
                        'total_chat_copy_events': model.get('total_chat_copy_events', 0)
                    }
                    records.append(record)
        
        df = pd.DataFrame(records)
        return df
    
    def adapt_metrics_chat_team(self, metrics_team):
        records = []
        for team, metric in metrics_team.items():
            records.append(self.adapt_metrics_chat_global(metric, team))
        return records

    def adapt_metrics_completitions_team(self, metrics_team):
        records = []
        for team, metric in metrics_team.items():
            records.append(self.adapt_metrics_completitions_global(metric, team))
        return records

    def adapt_metrics_completitions_global(self, metrics_global, team = None):
        """
        Adapt the global Copilot metrics data into a DataFrame with the specified format.

        Parameters:
            metrics_global (list): List of metrics data from extract_metrics_global.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - editor_name
                - model_name
                - total_engaged_users
                - total_chat
                - total_chat_insertion_events
                - total_chat_copy_events
        """
        records = []
        for metric in metrics_global:
            date = metric.get('date')
            copilot_ide_chat = metric.get('copilot_ide_code_completions', {})
            editors = copilot_ide_chat.get('editors', [])
            for editor in editors:
                editor_name = editor.get('name')
                models = editor.get('models', [])
                for model in models:
                    languages = model.get('languages', [])
                    for language in languages:
                        record = {
                            'team': team,
                            'date': date,
                            'editor_name': editor_name,
                            'model_name': model.get('name'),
                            'language': language.get('name'),
                            'total_code_lines_suggested': language.get('total_code_lines_accepted'),
                            'total_code_lines_accepted': model.get('total_code_lines_accepted', 0),
                            'total_engaged_users': model.get('total_engaged_users', 0)
                    }
                    records.append(record)
        
        df = pd.DataFrame(records)
        return df

