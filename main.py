from src.common import common
import configparser, argparse


parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.cfg", encoding ="utf-8")
    jiraToken = args.jira_token

    parameters = {
        "jira_token": args.jira_token,
        "project_key": "GO-DEVOPS"
    }

    exporter = common.ExporterFactory("JiraCloud")
    exporter.initialize_data(config,parameters)
    exporter.extract_data()