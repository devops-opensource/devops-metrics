import pandas as pd


class CsvLoader:
    def __init__(self, config):
        self._prefix = config["CSV"]["csv_filename_prefix"]

    def loadReleasesFromDf(self, df):
        csv_name = self._prefix + "_releases.csv"
        with open(csv_name, "w", encoding="UTF-8", newline=""):
            df.to_csv(csv_name, index=False)

    def loadStatusChangesFromDf(self, df):
        csv_name = self._prefix + "_status_changes.csv"
        with open(csv_name, "w", encoding="UTF-8", newline=""):
            df.to_csv(csv_name, index=False)
