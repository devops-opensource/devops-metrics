import pandas as pd

class TransformStatusChanges:

    _release_management = pd.DataFrame()
    _creation_status = ""
    _released_status = ""
    _closed_statuses = []

    def __init__(self, config, release_management):
        self._release_management = release_management
        self._creation_status = config["JIRA_CLOUD"]["jira_creation_status"]
        self._released_status = config["JIRA_CLOUD"]["jira_released_status"]
        self._closed_statuses = config["JIRA_CLOUD"]["jira_closed_statuses"].split(",")
    
    def transform_status_changes(self,df_status_changes):
        if(df_status_changes.empty):
            return pd.DataFrame()
        df_status_changes["to_date"] = pd.to_datetime(df_status_changes["to_date"], utc=True, errors="coerce").dt.tz_convert(None)
        df_status_changes["creation_date"] = pd.to_datetime(df_status_changes["creation_date"], utc=True, errors="coerce").dt.tz_convert(None)
        df_status_changes["from_date"] = df_status_changes.sort_values(["to_date"]).groupby("key")["to_date"].shift()
        df_status_changes["from_date"] = df_status_changes["from_date"].fillna(df_status_changes["creation_date"])
        df_status_changes.loc[df_status_changes.sort_values(["to_date"]).groupby("key")["from_status"].head(1).index, "from_status"] = self._creation_status
        
        df_status_changes["event_type"] = "status_change"

        df_status_changes = self.add_transition_to_released_status(df_status_changes)
        df_status_changes["control_date"] = df_status_changes["to_date"]
        
        return df_status_changes

    def add_transition_to_released_status(self,df_status_changes):
        df_closed = df_status_changes[df_status_changes["to_status"].isin(self._closed_statuses)]
        df_closed_dedup = df_closed.loc[df_closed.groupby("key")["to_date"].transform("max") == df_closed["to_date"]]

        df_released = pd.DataFrame()
        for row in df_closed_dedup.itertuples():
            versions = row.version.split(",")
            df_version = self._release_management
            dates = df_version[df_version["name"].isin(versions)][["release_date","name"]].dropna()
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