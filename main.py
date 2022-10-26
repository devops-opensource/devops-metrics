import configparser, argparse
from src.extractor.jiracloud_extractor import JiraCloud
from src.loader.csv_loader import CsvLoader
from src.loader.mysql_loader import MySqlLoader

parser = argparse.ArgumentParser()
parser.add_argument("jira_token")
parser.add_argument("mysql_password")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read("./config.default.cfg", encoding ="utf-8")

    jira_exporter = JiraCloud(config, args.jira_token, "CART")
    csv_loader = CsvLoader(config)
    mysql_loader = MySqlLoader(config, args.mysql_password)
    
    # Extract and Transform status changes and release
    print("Extract JIRA data then Transform as status_changes and releases")
    status_changes_df = jira_exporter.get_status_changes()
    releases_df = jira_exporter.get_release_management()

    # Load as CSV
    print("Load status_changes and releases as CSV")
    csv_loader.loadStatusChangesFromDf(status_changes_df)
    csv_loader.loadReleasesFromDf(releases_df)
    
    # Load as SQL
    print("Load status_changes and releases as SQL")
    mysql_loader.loadStatusChangesFromDf(status_changes_df)
    mysql_loader.loadReleasesFromDf(releases_df)
    
    print("Job done !")