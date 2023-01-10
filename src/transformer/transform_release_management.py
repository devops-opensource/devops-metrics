import pandas as pd

class TransformReleaseManagement:

    def transform_release_management(self, df_versions):
        if(df_versions.empty):
            return pd.DataFrame()
        df_versions_released = df_versions[df_versions["released"] == True]
        if ("release_date" in df_versions_released):
            df_versions_released.loc[:,"release_date"] = pd.to_datetime(df_versions_released["release_date"], utc=True, errors="coerce").dt.tz_convert(None)
        else:
            df_versions_released["release_date"] = None
        if ("start_date" in df_versions_released):
            df_versions_released["start_date"] = pd.to_datetime(df_versions_released["start_date"], utc=True, errors="coerce").dt.tz_convert(None)
        else:
            df_versions_released["start_date"] = None

        df_versions_released["event_type"] = "release_management"
        df_versions_released["control_date"] = df_versions_released["release_date"]

        return df_versions_released