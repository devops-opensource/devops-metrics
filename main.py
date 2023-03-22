import configparser
import argparse
from src.extractor.jiracloud_exporter import JiracloudExporter
from src.loader.csv_loader import CsvLoader
from src.loader.mysql_loader import MySqlLoader
from src.common import common
from src.transformer.transform_release_management import (
    TransformReleaseManagement,
)
from src.transformer.transform_status_change import TransformStatusChanges

parser = argparse.ArgumentParser()
parser.add_argument("config_file")
parser.add_argument("Exporter", type=str, help="Loader type: JiraCloud")
parser.add_argument("Loader", type=str, help="Loader type: CSV or MYSQL")
args = parser.parse_args()

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(args.config_file, encoding="utf-8")

    exporter_name = args.Exporter
    exporter = common.ExporterFactory(exporter_name)

    loader_name = args.Loader
    loader = common.LoaderFactory(loader_name)
    try:
        exporter.initialize_data(config)
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
    raw_data = exporter.extract_data()
    adapted_data = exporter.adapt_data(raw_data)
    release_transformer = TransformReleaseManagement()
    df_release_management = release_transformer.transform_release_management(
        adapted_data["versions"]
    )

    status_changes_transformer = TransformStatusChanges(
        config, df_release_management
    )
    df_status_cnhages = status_changes_transformer.transform_status_changes(
        adapted_data["status_changes"]
    )
    df_dict = {
        "status_changes": df_status_cnhages,
        "releases": df_release_management,
    }

    loader.load_data(df_dict)

    print("Job done !")
