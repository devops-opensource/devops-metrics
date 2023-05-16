import pandas as pd
from src.common import common


class TransformStatusChanges:
    _release_management = pd.DataFrame()
    _creation_status = ""
    _released_status = ""
    _closed_statuses = []

    def __init__(self, config, pivot_management):
        self._pivot_management = pivot_management
        self._creation_status = config["JIRA_CLOUD"]["jira_creation_status"]
        self._released_status = config["JIRA_CLOUD"]["jira_released_status"]
        self._closed_statuses = config["JIRA_CLOUD"][
            "jira_closed_statuses"
        ].split(",")
        if pivot_management["event_type"].iloc[0] == "epic_management":
            self._use_version = False
        else:
            self._use_version = True

    def transform_status_changes(self, df_status_changes):
        if df_status_changes.empty:
            return pd.DataFrame()
        df_status_changes = common.convert_column_to_datetime(
            "to_date", df_status_changes
        )
        df_status_changes = common.convert_column_to_datetime(
            "creation_date", df_status_changes
        )
        df_status_changes["from_date"] = (
            df_status_changes.sort_values(["to_date"])
            .groupby("key")["to_date"]
            .shift()
        )
        df_status_changes["from_date"] = df_status_changes["from_date"].fillna(
            df_status_changes["creation_date"]
        )
        df_status_changes.loc[
            df_status_changes.sort_values(["to_date"])
            .groupby("key")["from_status"]
            .head(1)
            .index,
            "from_status",
        ] = self._creation_status

        if self._use_version:
            # We add +1 to the id because the index 
            # is not taken into account in this case
            # But will be when going through the rows
            #  of the dataframe in add_transition_to_released_status
            pivot_column_id = df_status_changes.columns.get_loc("version") + 1
        else:
            pivot_column_id = (
                df_status_changes.columns.get_loc("parent_key") + 1
            )

        df_status_changes = self.add_transition_to_released_status(
            df_status_changes, pivot_column_id
        )
        df_status_changes["control_date"] = df_status_changes["to_date"]

        return df_status_changes

    def add_transition_to_released_status(
        self, df_status_changes, pivot_column_id
    ):
        df_closed = df_status_changes[
            df_status_changes["to_status"].isin(self._closed_statuses)
        ]
        df_closed_dedup = df_closed.loc[
            df_closed.groupby("key")["to_date"].transform("max")
            == df_closed["to_date"]
        ]

        df_released = pd.DataFrame()
        for row in df_closed_dedup.itertuples():
            df_pivots = self._pivot_management
            pivot = row[pivot_column_id].split(",")
            dates = df_pivots[df_pivots["name"].isin(pivot)][
                ["release_date", "name"]
            ].dropna()
            if len(dates) != 0:
                min_id = dates["release_date"].idxmin()
                new_row = df_closed_dedup.loc[[row.Index]].copy()
                new_row["from_status"] = new_row["to_status"]
                new_row["from_date"] = new_row["to_date"]
                new_row["to_status"] = self._released_status
                new_row["to_date"] = dates.loc[min_id]["release_date"]
                new_row["release_version"] = dates.loc[min_id]["name"]
                df_released = pd.concat([df_released, new_row])
        df_status_changes = pd.concat([df_status_changes, df_released])
        return df_status_changes
