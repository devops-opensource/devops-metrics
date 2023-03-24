from src.extractor import exporter, jiracloud_exporter, github_exporter
from src.loader import mysql_loader, csv_loader, loader
import pandas as pd
from functools import wraps
import time

def execution_time(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} '
              + 'Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {"JiraCloud": jiracloud_exporter.JiracloudExporter,
                  "GitHub": github_exporter.GithubExporter}
    return localizers[type]()


def LoaderFactory(type) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "MYSQL": mysql_loader.MySqlLoader,
        "CSV": csv_loader.CsvLoader,
    }
    return localizers[type]()


def convert_column_to_datetime(column, df):
    if column in df:
        df[column] = pd.to_datetime(
            df[column], utc=True, errors="coerce"
        ).dt.tz_convert(None)
    else:
        df[column] = None
    return df

def df_drop_and_rename_columns(self, dataframe, columns_mapping):
        for col in dataframe.columns:
            if col not in columns_mapping:
                dataframe = dataframe.drop(columns=col)
        dataframe = dataframe.rename(columns=columns_mapping)
        return dataframe

