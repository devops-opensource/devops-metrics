import pandas as pd
from src.common import column_to_datetime
from src.common import rename_and_drop_fields

class TransformCommits:
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