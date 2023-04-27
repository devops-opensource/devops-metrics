from src.transformer.transformer import Transformer
from src.common import common
import pandas as pd


class VersionControlTransformer(Transformer):
    def initialize_data(self, config):
        self.config = config

    def transform_data(self, adapted_data):
        df_pulls = self.transform_pull_requests(adapted_data["df_pulls"])
        df_commits = self.transform_commits(adapted_data["df_commits"])
        df_reviews = self.transform_reviews(adapted_data["df_reviews"])
        df_events = self.transform_pr_to_event(
            df_pulls, df_commits, df_reviews)
        df_dict = {
            "pulls": df_pulls,
            "commits": df_commits,
            "reviews": df_reviews,
            "pr_events": df_events
        }
        return df_dict

    def transform_pull_requests(self, df_pulls):
        df_pulls = common.convert_column_to_datetime("created", df_pulls)
        df_pulls = common.convert_column_to_datetime("closed", df_pulls)
        df_pulls = common.convert_column_to_datetime("merged", df_pulls)
        return df_pulls

    def transform_commits(self, df_commits):
        df_commits = common.convert_column_to_datetime(
            "commit_date", df_commits
        )
        return df_commits

    def transform_reviews(self, df_reviews):
        df_reviews = common.convert_column_to_datetime(
            "submitted_at", df_reviews
        )
        return df_reviews

    def transform_pr_to_event(self, df_pulls, df_commits, df_reviews):
        df_created_event = df_pulls[["repo", "number", "created"]]
        df_created_event["event_type"] = "Creation"
        df_created_event = df_created_event.rename(
            columns={"created": "timestamp"})

        df_merged_event = df_pulls[["repo", "number", "merged"]]
        df_merged_event["event_type"] = "Merge"
        df_merged_event = df_merged_event.rename(
            columns={"merged": "timestamp"})

        df_first_commit_event = df_commits.sort_values(
            "commit_date").groupby(["repo", "number"]).first()
        df_first_commit_event = df_first_commit_event.reset_index()
        df_first_commit_event = df_first_commit_event[[
            "repo", "number", "commit_date"]]
        df_first_commit_event["event_type"] = "First Commit"
        df_first_commit_event = df_first_commit_event.rename(
            columns={"commit_date": "timestamp"})

        df_review_event = df_reviews[["repo", "number", "submitted_at"]]
        df_review_event["event_type"] = "Review"
        df_review_event = df_review_event.rename(
            columns={"submitted_at": "timestamp"})

        df_events = pd.concat(
            [df_created_event, df_merged_event, df_first_commit_event, df_review_event])
        return df_events
