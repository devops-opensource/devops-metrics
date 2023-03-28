from src.transformer.transformer import Transformer
import pandas as pd
from src.common import common

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
        df_pulls = common.convert_column_to_datetime("created", df_pulls)
        df_pulls = common.convert_column_to_datetime("closed", df_pulls)
        df_pulls = common.convert_column_to_datetime("merged", df_pulls)
        return df_pulls
    
    def transform_commits(self, df_commits):
        df_commits = common.convert_column_to_datetime("commit_date", df_commits)
        return df_commits
    
    def transform_reviews(self, df_reviews):
        df_reviews = common.convert_column_to_datetime("submitted_at", df_reviews)
        return df_reviews