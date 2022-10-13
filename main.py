from src.common import common
import configparser, argparse
import jirascript as jira_exractor

parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.cfg", encoding ="utf-8")
    jiraToken = args.jira_token

    project_list = config.get("JIRA", "jira_project_keys").split(",")

    for project in project_list:
        jira_exporter = jira_exractor.JiraCloud(config, jiraToken, project)
        status_changes = jira_exporter.get_status_changes()
        # versions = jira_exporter.get_release_management()
        # print(versions)

    # parameters = {
    #     "jira_token": args.jira_token,
    #     "project_key": "GO-DEVOPS"
    # }

    # exporter = common.ExporterFactory("JiraCloud")
    # exporter.initialize_data(config,parameters)
    # exporter.extract_data()
