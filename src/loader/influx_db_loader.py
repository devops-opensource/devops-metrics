from __future__ import annotations

import pandas as pd

from src.loader import loader


class InfluxDBLoader(loader.Loader):
    """
    The Creator class declare the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    def initialize_data(self, config, parameters):
        self.username = config["INFLUXDB"]["username"]
        self.password = parameters["password"]
        self._base_url = config["INFLUXDB"]["base_url"]

    def load_data(self):
        print("Data Loader")
        return []