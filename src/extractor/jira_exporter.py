from __future__ import annotations
from src.extractor import exporter

import pandas as pd


class JiraExporter(exporter.Exporter):
    """
    The Creator class declare the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """
    def initialize_data(self, config, parameters):
        self._email = config["JIRA_CLOUD"]["jira_user_email"]
        self._token = parameters["jira_token"]
        self._jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self._project_key = parameters["project_key"]

    def extract_data(self):
        return []

    def adapt_data(self):
        return []
