from src.extractor import exporter, jira_exporter
from src.loader import mysql_loader, csv_loader,loader


def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {
        "JiraCloud": jira_exporter.JiraExporter
    }
    return localizers[type]()


def LoaderFactory(type) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "MYSQL": mysql_loader.MySqlLoader,
        "CSV": csv_loader.CsvLoader
    }
    return localizers[type]()