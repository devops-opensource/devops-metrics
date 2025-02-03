import requests
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from configparser import ConfigParser
from src.extractor.exporter import Exporter

pd.options.mode.chained_assignment = None  # default='warn'


class GithubCopilotExporter(Exporter):
    github_url: str
    github_org: str
    github_token: str

    def initialize_data(self, config: ConfigParser) -> None:
        self.github_url = config["GITHUB"]["github_url"]
        self.github_org = config["GITHUB"]["github_org"]
        self.github_token = config["GITHUB"]["github_token"]

        # For future reference if the need for mappings arises
        #with open("src/extractor/github_mappings.json") as json_file:
        #    self.mappings = json.load(json_file)
        #self.commits = dict()

    def create_session(self) -> requests.Session:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization" : "Bearer " + self.github_token
        }
        session = requests.Session()
        #session.auth = (self.github_user, self.github_token)
        session.headers.update(headers)
        return session

    def execute_paginated_request(self, endpoint: str, parameters: Dict[str, Any] = {"per_page": 100}) -> List[Dict[str, Any]]:
        """
        Generic method to call any GitHub endpoint with pagination.
        
        Args:
            endpoint: API endpoint path
            parameters: Query parameters for the request
            
        Returns:
            List of results from all pages
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
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
            print(f"Error making paginated request to {endpoint}: {str(e)}")
            raise

    def execute_simple_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Simple method without pagination to call any GitHub endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.github_url}/{endpoint}"
        try:
            with self.create_session() as session:
                r = session.get(url)
                r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            raise

    def extract_data(self) -> Dict[str, Any]:
        teams = self.extract_teams()
        metrics_per_team = self.extract_metrics_per_team(teams)
        metrics_global = self.extract_metrics_global()

        daily_active_users = self.extract_daily_active_users()
        # average active users calculated using raw daily_active_users data in the transformer
        new_seats_added, inactive_users = self.extract_seats_information()
        return {
            "metrics_per_team": metrics_per_team,
            "metrics_global": metrics_global,
        }
    
    def extract_metrics_per_team(self, teams: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve Copilot metrics for each team and store them in a dict
        keyed by the team's slug.

        Args:
            teams (list): List of team dictionaries containing team information
                         Each team dict must include a 'slug' key

        Returns:
            dict: Dictionary mapping team slugs to their Copilot metrics
                 {team_slug: metrics_list}

        Raises:
            requests.exceptions.RequestException: If any GitHub API request fails
            KeyError: If a team dict is missing the required 'slug' field
        """
        team_metrics = {}
        for team in teams:
            try:
                endpoint = f"orgs/{self.github_org}/teams/{team['slug']}/copilot/metrics"
                metrics = self.execute_paginated_request(endpoint)
                if metrics:  # Only add teams that have metrics
                    team_metrics[team['slug']] = metrics
                else:
                    print(f"No Copilot metrics found for team {team['slug']}")
            except KeyError:
                print(f"Team dictionary missing required 'slug' field: {team}")
                raise
            except requests.exceptions.RequestException as e:
                print(f"Failed to get metrics for team {team.get('slug', 'UNKNOWN')}: {str(e)}")
                raise

        if not team_metrics:
            print(f"Warning: No team metrics found for any teams in {self.github_org}")
            
        return team_metrics
    
    def extract_metrics_global(self) -> List[Dict[str, Any]]:
        """
        Retrieve Copilot metrics at the organization (global) level.
        This is a high-level summary of metrics for the entire org.

        Returns:
            list: List of dictionaries containing global Copilot metrics for the organization
                  Each dict contains metrics like active users, suggestions accepted, etc.

        Raises:
            requests.exceptions.RequestException: If the GitHub API request fails
        """
        endpoint = f"orgs/{self.github_org}/copilot/metrics"
        try:
            global_metrics = self.execute_paginated_request(endpoint)
            
            if not global_metrics:
                print(f"Warning: No global Copilot metrics found for organization {self.github_org}")
                
            return global_metrics
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching global Copilot metrics: {str(e)}")
            raise
    
    def extract_daily_active_users(self) -> Dict[str, int]:
        # Note: there is a discrepency between the active users returned by /metrics and /usage
        # Note 2: active users is typically more elevated than the alternative field "engaged_users" since it tracks people who may have logged in but not used the tool
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
        """
        Retrieve all active teams from the GitHub organization.
        
        Returns:
            list: List of team dictionaries containing team information
                  Each team dict includes: 'slug', 'name', 'description', etc.
        
        Raises:
            requests.exceptions.RequestException: If the GitHub API request fails
        """
        endpoint = f"orgs/{self.github_org}/teams"
        try:
            teams = self.execute_paginated_request(endpoint)
            # Filter out archived/inactive teams if they exist
            active_teams = [team for team in teams if not team.get('archived', False)]
            
            if not active_teams:
                print(f"Warning: No active teams found in organization {self.github_org}")
            
            return active_teams
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching teams from GitHub: {str(e)}")
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
        """
        Adapt Copilot chat metrics data into a DataFrame.

        Parameters:
            metrics_global (list): List of metrics data containing chat statistics
            team (str, optional): Team name for the metrics

        Returns:
            pd.DataFrame: DataFrame with columns:
                - team
                - date
                - editor_name
                - model_name
                - total_engaged_users
                - total_chat
                - total_chat_insertion_events
                - total_chat_copy_events
        """
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
                print(f"Error processing chat metric: {e}")
                continue
        
        return pd.DataFrame(records)
    
    def adapt_metrics_chat_team(self, metrics_team: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Adapt team-level chat metrics into a single DataFrame.

        Parameters:
            metrics_team (dict): Dictionary of team metrics keyed by team name

        Returns:
            pd.DataFrame: Combined DataFrame of all team chat metrics
        """
        # Pre-allocate list for better performance
        dfs = []
        for team, metric in metrics_team.items():
            try:
                df = self.adapt_metrics_chat_global(metric, team)
                dfs.append(df)
            except Exception as e:
                print(f"Error processing team {team}: {e}")
                continue
        
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def adapt_metrics_completions_global(self, metrics_global: List[Dict[str, Any]], team: Optional[str] = None) -> pd.DataFrame:
        """
        Adapt GitHub Copilot code completion metrics data into a structured DataFrame.

        This method processes raw completion metrics data from GitHub Copilot and transforms
        it into a tabular format. It extracts information about code suggestions, acceptance rates,
        and user engagement across different editors, models and programming languages.

        Parameters:
            metrics_global (List[Dict[str, Any]]): List of metrics data containing completion statistics.
                Each dict should have 'date' and 'copilot_ide_code_completions' fields.
            team (Optional[str]): Team identifier for the metrics. If None, indicates global metrics.

        Returns:
            pd.DataFrame: DataFrame containing processed completion metrics with columns:
                - team: Team identifier (str)
                - date: Date of the metrics (datetime)
                - editor_name: Name of the editor used (str)
                - model_name: Name of the Copilot model (str) 
                - language: Programming language (str)
                - total_code_lines_suggested: Number of lines suggested by Copilot (int)
                - total_code_lines_accepted: Number of suggested lines accepted by users (int)
                - total_engaged_users: Number of users who used completions (int)

        Raises:
            Exception: If there are errors processing individual metrics entries
        """
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
                print(f"Error processing completion metric: {e}")
                continue
        
        return pd.DataFrame(records)

    def adapt_metrics_completions_team(self, metrics_team: Dict[str, List[Dict[str, Any]]]) -> pd.DataFrame:
        """
        Adapt team-level completion metrics into a single DataFrame.

        Parameters:
            metrics_team (dict): Dictionary of team metrics keyed by team name

        Returns:
            pd.DataFrame: Combined DataFrame of all team completion metrics
        """
        dfs = []
        for team, metric in metrics_team.items():
            try:
                df = self.adapt_metrics_completions_global(metric, team)
                dfs.append(df)
            except Exception as e:
                print(f"Error processing team {team}: {e}")
                continue
        
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

