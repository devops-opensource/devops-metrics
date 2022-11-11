import configparser
import argparse
from src.extractor.jiracloud_extractor import JiraCloud
from src.loader.csv_loader import CsvLoader
from src.loader.mysql_loader import MySqlLoader
from src.common import common

parser = argparse.ArgumentParser()
parser.add_argument("config_file")
parser.add_argument("Loader", type=str, help="Loader type: CSV or MYSQL")
args = parser.parse_args()

if __name__ == "__main__": 
    config = configparser.ConfigParser()
    config.read(args.config_file, encoding="utf-8")

    loader_name = args.Loader
    loader = common.LoaderFactory(loader_name)

    try:
        jira_exporter = JiraCloud(config)
    except Exception as err:
        print(err)
        quit("Unable to connect to JIRA project")

    try:
        loader.initialize_data(config)
    except Exception as err:
        print(err)
        quit("Unable to connect to mysql database")

    # Extract and Transform status changes and release
    print("Extract JIRA data then Transform as status_changes and releases")
    df_dict = {}
    df_dict["status_changes"] = jira_exporter.get_status_changes()
    df_dict["releases"] = jira_exporter.get_release_management()

    loader.load_data(df_dict)

    print("Job done !")