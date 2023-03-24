import pandas as pd
from src.common import column_to_datetime
from src.common import rename_and_drop_fields

class TransformPullRequest:
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