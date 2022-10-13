import jirascript as jira_export
import configparser, argparse

parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.cfg", encoding ="utf-8")
    jiraToken = args.jira_token

    project_list = config.get("JIRA", "jira_project_keys").split(",")

    for project in project_list:
        jira_exporter = jira_export.JiraCloud(config, jiraToken, project)

        versions = jira_exporter.get_release_management()
        print(versions)