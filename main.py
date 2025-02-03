import configparser
import argparse
from src.common import common

parser = argparse.ArgumentParser()
parser.add_argument("config_file")
parser.add_argument("Exporter", type=str, help="Loader type: GitHub")
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
    print(f"Extract {exporter_name}")
    raw_data = exporter.extract_data()
    print("Extract completed")

    print(f"Adapt {exporter_name}")
    adapted_data = exporter.adapt_data(raw_data)
    print("Adapt completed")
    
    print(f"Transform {exporter_name}")
    df_dict = transformer.transform_data(adapted_data)
    print("Transform completed")

    print(f"Load {loader_name}")
    loader.load_data(df_dict)
    print("Load completed")

    print("Job done !")

