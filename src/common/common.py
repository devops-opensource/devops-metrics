from src.extractor import exporter, jiracloud_exporter
from src.loader import mysql_loader, csv_loader, splunk_loader, loader
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
    localizers = {"JiraCloud": jiracloud_exporter.JiracloudExporter}
    return localizers[type]()


def LoaderFactory(type) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "MYSQL": mysql_loader.MySqlLoader,
        "CSV": csv_loader.CsvLoader,
        "SPLUNK": splunk_loader.SplunkLoader
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
