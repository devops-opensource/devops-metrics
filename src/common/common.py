from src.extractor import exporter, jira_exporter
from src.loader import influx_db_loader, loader

def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {
        "JiraCloud": jira_exporter.JiraExporter
    }
 
    return localizers[type]()


def ImporterFactory(type) -> loader.Loader:
    """Factory Method"""
    localizers = {
        "InfluxDB": influx_db_loader.InfluxDBLoader
    }

    return localizers[type]()
