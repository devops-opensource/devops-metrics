from src.transformer.transformer import Transformer
import pandas as pd
from typing import Dict, List

class CopilotTransformer(Transformer):
    def initialize_data(self, config: dict) -> None:
        self.config = config

    def transform_data(self, adapted_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        transformed: Dict[str, pd.DataFrame] = {}
        # Transform each dataframe using corresponding method
        for key, df in adapted_data.items():
            if key == 'df_daily_active_users':
                transformed[key] = df
                transformed['df_average_active_users'] = self.transform_average_active_users(df['active_users'])
            elif key == 'df_seats':
                transformed[key] = df
            elif 'metrics_chat' in key:
                transform_method = self.transform_chat_metrics_team if 'team' in df.columns else self.transform_chat_metrics_global
                transformed[key] = transform_method(df)
            elif 'metrics_completion' in key:
                transform_method = self.transform_completion_metrics_team if 'team' in df.columns else self.transform_completion_metrics_global
                transformed[key] = transform_method(df)

        return transformed
    
    def sanitize_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean metrics by replacing infinite and NaN values with 0
        """
        df = df.replace([float('inf'), float('-inf')], 0)
        df = df.fillna(0)
        return df
    
    def transform_average_active_users(self, daily_active_users: pd.DataFrame) -> pd.DataFrame:
        average_active_users = daily_active_users['active_users'].mean().astype(int)
        df = pd.DataFrame({'average_active_users': [average_active_users]})
        return df

    def transform_chat_metrics(self, metrics_chat: pd.DataFrame, aggregation_list: List[str]) -> pd.DataFrame:
        """
        Transform chat metrics to calculate:
        1. Average chats per user (total_chat / total_engaged_users)
        2. Chat acceptance rate ((total_chat_copy_events + total_chat_insertion_events) / total_chat)
        """
        chat_metrics = metrics_chat.groupby(aggregation_list).agg({
            'total_chat': 'sum',
            'total_engaged_users': 'sum',
            'total_chat_copy_events': 'sum',
            'total_chat_insertion_events': 'sum'
        }).reset_index()
        
        chat_metrics['chat_per_user'] = (
            chat_metrics['total_chat'] / 
            chat_metrics['total_engaged_users']
        )
        chat_metrics['chat_acceptance_rate'] = (
            (chat_metrics['total_chat_copy_events'] + 
             chat_metrics['total_chat_insertion_events']) / 
            chat_metrics['total_chat']
        )
        
        return self.sanitize_metrics(chat_metrics)

    def transform_chat_metrics_team(self, metrics_chat_team: pd.DataFrame) -> pd.DataFrame:
        """
        Transform team chat metrics by date
        """
        return self.transform_chat_metrics(metrics_chat_team, ['team', 'date'])

    def transform_chat_metrics_global(self, metrics_global: pd.DataFrame) -> pd.DataFrame:
        """
        Transform global chat metrics by date
        """
        return self.transform_chat_metrics(metrics_global, ['date'])

    def transform_completion_metrics(self, metrics_completion: pd.DataFrame, aggregation_list: List[str]) -> pd.DataFrame:
        """
        Transform completion metrics by date to calculate:
        1. Code acceptance rate (total_code_acceptances / total_code_suggestions)
        2. Lines acceptance rate (total_code_lines_accepted / total_code_lines_suggested)
        """
        metrics_completion = metrics_completion.groupby(aggregation_list).agg({
            'total_code_lines_accepted': 'sum',
            'total_code_lines_suggested': 'sum'
        }).reset_index()

        metrics_completion['completion_acceptance_rate'] = (
            metrics_completion['total_code_lines_accepted'] / 
            metrics_completion['total_code_lines_suggested']
        )

        return self.sanitize_metrics(metrics_completion)

    def transform_completion_metrics_team(self, metrics_completion_team: pd.DataFrame) -> pd.DataFrame:
        """
        Transform team completion metrics by date to calculate:
        1. Code acceptance rate (total_code_acceptances / total_code_suggestions)
        2. Lines acceptance rate (total_code_lines_accepted / total_code_lines_suggested)
        """
        return self.transform_completion_metrics(metrics_completion_team, ['team', 'date', 'language'])

    def transform_completion_metrics_global(self, metrics_completion_global: pd.DataFrame) -> pd.DataFrame:
        """
        Transform global completion metrics by date using the same calculations as team metrics
        but for the entire organization
        """
        return self.transform_completion_metrics(metrics_completion_global, ['date', 'language'])
