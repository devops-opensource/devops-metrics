from src.common import common
import configparser, argparse
import jirascript as jira_exractor

parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
parser.add_argument("influxdb_password")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.cfg", encoding ="utf-8")
    jira_token = args.jira_token

    exporter_parameters = {
        "jira_token": jira_token,
        "project_key": "GO-DEVOPS"
    }

    for project in project_list:
        jira_exporter = jira_exractor.JiraCloud(config, jiraToken, project)
        status_changes = jira_exporter.get_status_changes()
        versions = jira_exporter.get_release_management()
    # exporter = common.ExporterFactory("JiraCloud")
    # exporter.initialize_data(config, exporter_parameters)
    # exporter.extract_data()

    # importer_parameters = {
    #     "password": args.influxdb_password,
    # }
    
    # importer = common.ImporterFactory("InfluxDB")
    # importer.initialize_data(config, importer_parameters)
    # importer.adapt_data()
    # importer.load_data()
