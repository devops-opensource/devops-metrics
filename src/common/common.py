from src.extractor import exporter, jiracloud_exporter
from src.loader import mysql_loader, csv_loader, loader
import pandas as pd


def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {
        "JiraCloud": jiracloud_exporter.JiracloudExporter
    }
    return localizers[type]()


def LoaderFactory(type) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "MYSQL": mysql_loader.MySqlLoader,
        "CSV": csv_loader.CsvLoader
    }
    return localizers[type]()


def convert_column_to_datetime(column, df):
    if (column in df):
        df[column] = pd.to_datetime(
            df[column], utc=True, errors="coerce").dt.tz_convert(None)
    else:
        df[column] = None
    return df
