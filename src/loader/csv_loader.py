import pandas as pd
from src.loader import loader

class CsvLoader(loader.Loader):
    def initialize_data(self, config):
        self._prefix = config["CSV"]["csv_filename_prefix"]

    def load_data(self, df_dict):
        for type, df in self.df_dict.items():
            df = pd.DataFrame(df_dict)
            csv_name = f"{self._prefix}_{type}.csv"
            with open(csv_name, "w", encoding="UTF-8", newline="") as csv:
                df.to_csv(csv, index=False)
                print(f"CSV file {csv_name} created")