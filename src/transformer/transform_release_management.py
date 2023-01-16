import pandas as pd

class TransformReleaseManagement:

    def transform_release_management(self, df_versions):
        if(df_versions.empty):
            return pd.DataFrame()
        df_versions_released = df_versions[df_versions["released"] == True]

        df_versions_released = self.convert_column_to_datetime("release_date", df_versions_released)
        df_versions_released = self.convert_column_to_datetime("start_date", df_versions_released)

        df_versions_released["event_type"] = "release_management"
        df_versions_released["control_date"] = df_versions_released["release_date"]

        return df_versions_released

    def convert_column_to_datetime(self, column, df):
        if (column in df):
            df[column] = pd.to_datetime(df[column], utc=True, errors="coerce").dt.tz_convert(None)
        else:
            df[column] = None
        return df
