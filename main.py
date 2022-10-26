import configparser, argparse
import jirascript as jira_exractor
from mysql_loader import MySqlLoader

parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
parser.add_argument("mysql_password")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.gologic.cfg", encoding ="utf-8")
    jira_token = args.jira_token
    mysql_password = args.mysql_password

    jira_exporter = jira_exractor.JiraCloud(config, jira_token, "CART")
    status_changes_df = jira_exporter.get_status_changes()
    versions_df = jira_exporter.get_release_management()

    jira_exractor.df_to_csv(status_changes_df, "examples/CART_status_changes.csv")
    jira_exractor.df_to_csv(versions_df, "examples/CART_versions.csv")

    mysql_loader = MySqlLoader(config, mysql_password)
    mysql_loader.loadReleasesFromDf(versions_df)
    mysql_loader.loadStatusChangesFromDf(status_changes_df)