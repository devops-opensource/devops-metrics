import logging
import requests
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from configparser import ConfigParser
from src.extractor.exporter import Exporter

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

pd.options.mode.chained_assignment = None  # default='warn'


class GithubCopilotExporter(Exporter):

    def __init__(self):
        self.github_url: Optional[str] = None
        self.github_org: Optional[str] = None
        self.github_token: Optional[str] = None

    def initialize_data(self, config: ConfigParser) -> None:
        self.github_url = config["GITHUB"]["github_url"]
        self.github_org = config["GITHUB"]["github_org"]
        self.github_token = config["GITHUB"]["github_token"]

    def create_session(self) -> requests.Session:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.github_token
        }
        session = requests.Session()
        session.headers.update(headers)
        return session

    def execute_paginated_request(self, endpoint: str, parameters: Dict[str, Any] = {"per_page": 100}) -> List[Dict[str, Any]]:
        another_page = True
        url = f"{self.github_url}/{endpoint}"
        results = []

        try:
            while another_page:
                with self.create_session() as session:
                    r = session.get(url, params=parameters, verify=False)
                    r.raise_for_status()

                json_response = r.json()
                results.extend(json_response)

                if "next" in r.links:
                    url = r.links["next"]["url"]
                else:
                    another_page = False
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making paginated request to {endpoint}: {e}")
            raise

    def execute_simple_request(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.github_url}/{endpoint}"
        try:
            with self.create_session() as session:
                r = session.get(url)
                r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            raise

    def extract_data(self) -> Dict[str, Any]:
        teams = self.extract_teams()
        metrics_per_team = self.extract_metrics_per_team(teams)
        metrics_global = self.extract_metrics_global()

        daily_active_users = self.extract_daily_active_users()
        new_seats_added, inactive_users = self.extract_seats_information()
        return {
            "metrics_per_team": metrics_per_team,
            "metrics_global": metrics_global,
            "daily_active_users": daily_active_users,
            "new_seats_added": new_seats_added,
            "inactive_users": inactive_users,
        }

    def extract_metrics_per_team(self, teams: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        team_metrics = {}
        for team in teams:
            try:
                endpoint = f"orgs/{self.github_org}/teams/{team['slug']}/copilot/metrics"
                metrics = self.execute_paginated_request(endpoint)
                if metrics:
                    team_metrics[team['slug']] = metrics
                else:
                    logger.warning(f"No Copilot metrics found for team {team['slug']}")
            except KeyError:
                logger.error(f"Team dictionary missing required 'slug' field: {team}")
                raise
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get metrics for team {team.get('slug', 'UNKNOWN')}: {e}")
                raise

        if not team_metrics:
            logger.warning(f"Warning: No team metrics found for any teams in {self.github_org}")
            
        return team_metrics

    def extract_metrics_global(self) -> List[Dict[str, Any]]:
        endpoint = f"orgs/{self.github_org}/copilot/metrics"
        try:
            global_metrics = self.execute_paginated_request(endpoint)
            if not global_metrics:
                logger.warning(f"Warning: No global Copilot metrics found for organization {self.github_org}")
            return global_metrics
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching global Copilot metrics: {e}")
            raise

    def extract_daily_active_users(self) -> Dict[str, int]:
        endpoint = f"{self.github_org}/copilot/metrics"
        all_metrics = self.execute_paginated_request(endpoint)
        daily_active_users = {}
        for metric in all_metrics:
            daily_active_users[metric['date']] = metric['total_active_users']
        return daily_active_users

    def extract_seats_information(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        endpoint = f"{self.github_org}/copilot/billing"
        seats_information = self.execute_simple_request(endpoint)
        seats_information_breakdown = seats_information['seat_breakdown']
        return (
            {'added_this_cycle': seats_information_breakdown['added_this_cycle']},
            {'inactive_this_cycle': seats_information_breakdown['inactive_this_cycle']}
        )

    def extract_teams(self) -> List[Dict[str, Any]]:
        endpoint = f"orgs/{self.github_org}/teams"
        try:
            teams = self.execute_paginated_request(endpoint)
            active_teams = [team for team in teams if not team.get('archived', False)]
            if not active_teams:
                logger.warning(f"Warning: No active teams found in organization {self.github_org}")
            return active_teams
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching teams from GitHub: {e}")
            raise

    def adapt_data(self, raw_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        daily_active_users = raw_data["daily_active_users"]
        df_daily_active_users = self.adapt_daily_active_users(daily_active_users)
        
        added_seats, inactive_seats = raw_data["new_seats_added"], raw_data["inactive_users"]
        df_seats = self.adapt_seats_information(added_seats, inactive_seats)
    
        metrics_per_team = raw_data["metrics_per_team"] 
        df_metrics_chat_team = self.adapt_metrics_chat_team(metrics_per_team)
        df_metrics_completions_team = self.adapt_metrics_completions_team(metrics_per_team)

        metrics_global = raw_data["metrics_global"]
        df_metrics_chat_global = self.adapt_metrics_chat_global(metrics_global)
        df_metrics_completions_global = self.adapt_metrics_completions_global(metrics_global)

        return {
            "df_daily_active_users": df_daily_active_users,
            "df_seats": df_seats,
            "df_metrics_chat_team": df_metrics_chat_team,
            "df_metrics_completions_team": df_metrics_completions_team,
            "df_metrics_chat_global": df_metrics_chat_global,
            "df_metrics_completions_global": df_metrics_completions_global
        }

    def adapt_daily_active_users(self, daily_active_users: Dict[str, int]) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(daily_active_users, orient='index', columns=['active_users'])
        df.index = pd.to_datetime(df.index)
        df.index.name = 'date'
        df = df.reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df['active_users'] = df['active_users'].astype(int)
        return df

    def adapt_seats_information(self, added_seats: Dict[str, int], inactive_seats: Dict[str, int]) -> pd.DataFrame:
        df = pd.DataFrame({
            'added_seats': [added_seats['added_this_cycle']],
            'inactive_seats': [inactive_seats['inactive_this_cycle']]
        })
        return df
    
    def adapt_metrics_chat_global(self, metrics_global: List[Dict[str, Any]], team: Optional[str] = None) -> pd.DataFrame:
        records = []
        for metric in metrics_global:
            try:
                date = metric.get('date')
                chat_data = metric.get('copilot_ide_chat', {})
                for editor in chat_data.get('editors', []):
                    editor_name = editor.get('name')
                    for model in editor.get('models', []):
                        records.append({
                            'team': team,
                            'date': date,
                            'editor_name': editor_name,
                            'model_name': model.get('name'),
                            'total_engaged_users': model.get('total_engaged_users', 0),
                            'total_chat': model.get('total_chats', 0),
                            'total_chat_insertion_events': model.get('total_chat_insertion_events', 0),
                            'total_chat_copy_events': model.get('total_chat_copy_events', 0)
                        })
            except Exception as e:
                logger.error(f"Error processing chat metric: {e}")
                continue
        return pd.DataFrame(records)
    
    def adapt_metrics_chat_team(self, metrics_team: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        dfs = []
        for team, metric in metrics_team.items():
            try:
                df = self.adapt_metrics_chat_global(metric, team)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error processing team {team}: {e}")
                continue
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def adapt_metrics_completions_global(self, metrics_global: List[Dict[str, Any]], team: Optional[str] = None) -> pd.DataFrame:
        records = []
        for metric in metrics_global:
            try:
                date = metric.get('date')
                completion_data = metric.get('copilot_ide_code_completions', {})
                for editor in completion_data.get('editors', []):
                    editor_name = editor.get('name')
                    for model in editor.get('models', []):
                        for language in model.get('languages', []):
                            records.append({
                                'team': team,
                                'date': date,
                                'editor_name': editor_name,
                                'model_name': model.get('name'),
                                'language': language.get('name'),
                                'total_code_lines_suggested': language.get('total_code_lines_suggested', 0),
                                'total_code_lines_accepted': language.get('total_code_lines_accepted', 0),
                                'total_engaged_users': model.get('total_engaged_users', 0)
                            })
            except Exception as e:
                logger.error(f"Error processing completion metric: {e}")
                continue
        return pd.DataFrame(records)

    def adapt_metrics_completions_team(self, metrics_team: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        dfs = []
        for team, metric in metrics_team.items():
            try:
                df = self.adapt_metrics_completions_global(metric, team)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Error processing team {team}: {e}")
                continue
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
