import pandas as pd
from src.common import common


class TransformReleaseManagement:

    def transform_release_management(self, df_versions):
        if (df_versions.empty):
            return pd.DataFrame()
        df_versions_released = df_versions[df_versions["released"]]

        df_versions_released = common.convert_column_to_datetime(
            "release_date", df_versions_released)
        df_versions_released = common.convert_column_to_datetime(
            "start_date", df_versions_released)

        df_versions_released["event_type"] = "release_management"
        df_versions_released["control_date"] = df_versions_released["release_date"]

        return df_versions_released
