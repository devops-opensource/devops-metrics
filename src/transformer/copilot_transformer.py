from src.transformer.transformer import Transformer
import pandas as pd

# Currently Copilot data does not need transformation from the dictionaries via which it is extracted
# Placeholder class
# More advanced metrics (efficience plutot que utilisation) will likely require tranformation
class CopilotTransformer(Transformer):
    def initialize_data(self, config):
        self.config = config

    def transform_data(self, adapted_data):
        daily_active_users = adapted_data['df_daily_active_users']
        average_active_users = self.transform_average_active_users(adapted_data['df_daily_active_users'])
        metrics_chat_global = self.transform_chat_metrics_global(adapted_data['df_metrics_chat_global'])
        metrics_chat_team = self.transform_chat_metrics_team(adapted_data['df_metrics_chat_team'])
        metrics_completion_global = self.transform_completion_metrics_global(adapted_data['df_metrics_completion_global'])
        metrics_completion_team = self.transform_completion_metrics_team(adapted_data['df_metrics_completion_team'])
        df_seats = adapted_data['df_seats']
        df_dict = {
            "df_daily_active_users": daily_active_users,
            "df_average_active_users": average_active_users,
            "df_seats": df_seats,
            "df_metrics_chat_global": metrics_chat_global,  
            "df_metrics_chat_team": metrics_chat_team,
            "df_metrics_completion_global": metrics_completion_global,
            "df_metrics_completion_team": metrics_completion_team
        }
        return df_dict
    

    def transform_chat_metrics_global(self, metrics_global):
        """
        Transform global metrics by date using the same calculations as team metrics
        but for the entire organization
        """
        # Group by date and calculate sums
        global_metrics = metrics_global.groupby('date').agg({
            'total_chat': 'sum',
            'total_engaged_users': 'sum',
            'total_chat_copy_events': 'sum',
            'total_chat_insertion_events': 'sum'
        }).reset_index()
        
        # Calculate the metrics
        global_metrics['chat_per_user'] = (
            global_metrics['total_chat'] / 
            global_metrics['total_engaged_users']
        )
        global_metrics['chat_acceptance_rate'] = (
            (global_metrics['total_chat_copy_events'] + 
             global_metrics['total_chat_insertion_events']) / 
            global_metrics['total_chat']
        )
        
        # Replace infinities and NaN with 0
        global_metrics = global_metrics.replace([float('inf'), float('-inf')], 0)
        global_metrics = global_metrics.fillna(0)
        
        return global_metrics

    def transform_chat_metrics_team(self, metrics_chat_team):
        """
        Transform team metrics by date to calculate:
        1. Average chats per user (total_chat / total_engaged_users)
        2. Chat acceptance rate ((total_chat_copy_events + total_chat_insertion_events) / total_chat)
        """
        # Group by team and date, then calculate sums
        team_metrics = metrics_chat_team.groupby(['team', 'date']).agg({
            'total_chat': 'sum',
            'total_engaged_users': 'sum',
            'total_chat_copy_events': 'sum',
            'total_chat_insertion_events': 'sum'
        }).reset_index()
        
        # Calculate the metrics
        team_metrics['chat_per_user'] = (
            team_metrics['total_chat'] / 
            team_metrics['total_engaged_users']
        )
        team_metrics['chat_acceptance_rate'] = (
            (team_metrics['total_chat_copy_events'] + 
             team_metrics['total_chat_insertion_events']) / 
            team_metrics['total_chat']
        )
        
        # Replace infinities and NaN with 0
        team_metrics = team_metrics.replace([float('inf'), float('-inf')], 0)
        team_metrics = team_metrics.fillna(0)
        
        return team_metrics
    
    def transform_completion_metrics_team(self, metrics_completion_team):
        """
        Transform team completion metrics by date to calculate:
        1. Code acceptance rate (total_code_acceptances / total_code_suggestions)
        2. Lines acceptance rate (total_code_lines_accepted / total_code_lines_suggested)
        """
        # Group by team and date, then calculate sums
        team_metrics = metrics_completion_team.groupby(['team', 'date', 'language']).agg({
            'total_code_lines_accepted': 'sum',
            'total_code_lines_suggested': 'sum'
        }).reset_index()
        
        team_metrics['completion_acceptance_rate'] = (
            team_metrics['total_code_lines_accepted'] / 
            team_metrics['total_code_lines_suggested']
        )

        # Replace infinities and NaN with 0
        team_metrics = team_metrics.replace([float('inf'), float('-inf')], 0)
        team_metrics = team_metrics.fillna(0)
        
        return team_metrics

    def transform_completion_metrics_global(self, metrics_completion_global):
        """
        Transform global completion metrics by date using the same calculations as team metrics
        but for the entire organization
        """
        # Group by date and calculate sums
        global_metrics = metrics_completion_global.groupby(['date', 'language']).agg({
            'total_code_lines_accepted': 'sum',
            'total_code_lines_suggested': 'sum'
        }).reset_index()

        
        global_metrics['completion_acceptance_rate'] = (
            global_metrics['total_code_lines_accepted'] / 
            global_metrics['total_code_lines_suggested']
        )
        
        # Replace infinities and NaN with 0
        global_metrics = global_metrics.replace([float('inf'), float('-inf')], 0)
        global_metrics = global_metrics.fillna(0)
        
        return global_metrics

    def transform_average_active_users(self, daily_active_users):
        average_active_users = daily_active_users['active_users'].mean().astype(int)
        df = pd.DataFrame({'average_active_users': [average_active_users]})
        return df