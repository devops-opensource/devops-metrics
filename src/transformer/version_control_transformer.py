from transformer import Transformer
import pandas as pd
from src.common.common import convert_column_to_datetime

class VersionControlTransformer(Transformer):
    def initialize_data(self, config):
        self.config = config

    def transform_data(self, adapted_data):
        df_pulls = self.transform_pull_requests(adapted_data["df_pulls"])
        df_commits = self.transform_commits(adapted_data["df_commits"])
        df_reviews = self.transform_reviews(adapted_data["df_reviews"])
        df_dict = {
            "df_pulls": df_pulls,
            "df_commits": df_commits,
            "df_reviews": df_reviews 
        }
        return df_dict
    
    def transform_pull_requests(self, df_pulls):
        df_pulls = convert_column_to_datetime(df_pulls, "created")
        df_pulls = convert_column_to_datetime(df_pulls, "closed")
        df_pulls = convert_column_to_datetime(df_pulls, "merged")
        return df_pulls
    
    def transform_commits(self, df_commits):
        df_commits = convert_column_to_datetime(df_commits, "commit_date")
        return df_commits
    
    def transform_reviews(self, df_reviews):
        df_reviews = convert_column_to_datetime(df_reviews, "submitted_at")
        return df_reviews