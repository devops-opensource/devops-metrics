from src.extractor import exporter, jira_exporter
from src.loader import  loader, mysql_loader, csv_loader


def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {
        "JiraCloud": jira_exporter.JiraExporter
    }
    return localizers[type]()


def LoaderFactory(type,config) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "MySql": mysql_loader.MySqlLoader,
        "Csv": csv_loader.CsvLoader
    }
    return localizers[type](config)
