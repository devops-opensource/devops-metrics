from src.exporter import exporter, jira_exporter


def ExporterFactory(type) -> exporter.Exporter:
    """Factory Method"""
    localizers = {
        "JiraCloud": jira_exporter.JiraExporter
    }
 
    return localizers[type]()