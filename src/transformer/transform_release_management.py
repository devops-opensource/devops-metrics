import pandas as pd
from src.common import common


class TransformReleaseManagement:
    def transform_release_management(self, df_pivot):
        if df_pivot.empty:
            return pd.DataFrame()

        df_pivot_closed = df_pivot[df_pivot["released"]]

        df_pivot_closed = common.convert_column_to_datetime(
            "release_date", df_pivot_closed
        )
        df_pivot_closed = common.convert_column_to_datetime(
            "start_date", df_pivot_closed
        )
        df_pivot_closed["control_date"] = df_pivot_closed["release_date"]

        return df_pivot_closed
