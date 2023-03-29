import configparser
import argparse
from src.common import common

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

    transformer = common.TransformerFactory(exporter_name)

    loader_name = args.Loader
    loader = common.LoaderFactory(loader_name)
    try:
        exporter.initialize_data(config)
    except Exception as err:
        print(err)
        quit(f"Unable to connect to {args.Exporter}")

    try:
        transformer.initialize_data(config)
    except Exception as err:
        print(err)
        quit(f"Unable to create a transformer for {args.Exporter}")

    try:
        loader.initialize_data(config)
    except Exception as err:
        print(err)
        quit(f"Unable to connect to {args.Loader}")

    # Extract and Transform status changes and release
    print("Extract JIRA data then Transform as status_changes and releases")
    raw_data = exporter.extract_data()
    adapted_data = exporter.adapt_data(raw_data)
    df_dict = transformer.transform_data(adapted_data)

    loader.load_data(df_dict)

    print("Job done !")
