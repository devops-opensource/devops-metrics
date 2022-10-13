from src.common import common
import configparser, argparse


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

    exporter = common.ExporterFactory("JiraCloud")
    exporter.initialize_data(config, exporter_parameters)
    exporter.extract_data()

    importer_parameters = {
        "password": args.influxdb_password,
    }
    
    importer = common.ImporterFactory("InfluxDB")
    importer.initialize_data(config, importer_parameters)
    importer.adapt_data()
    importer.load_data()
