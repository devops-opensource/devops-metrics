import unittest
import json
import configparser
from unittest import mock
from src.extractor import jira_exporter as exporter

class TestJiraTransform(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read('config.test.cfg')
        self.jira_exporter = exporter.JiraCloud(config,"token","server","","")

    # def test_transform_versions(self):
    #     # prepare
    #     initial_version_data = json.load(open("tests/unit_test/data/release_management.json", "r"))
    #     expected_release_management_json = json.load(open("tests/unit_test/data/release_management.json", "r"))

    #     # execute
    #     transformed_versions = self.jira_exporter.transform_versions(self.initial_version_data)
    #     transformed_versions_json = self.jira_exporter.dataframe_to_json(transformed_versions)

    #     # assert
    #     self.assertListEqual(transformed_versions_json,expected_release_management_json)

    # @mock.patch("src.extractor.jiracloud_extractor")
    # def test_transform_changelogs(self, mock_get_versions):
    #     # prepare
    #     status_change_json = json.load(open("tests/unit_test/data/status_change_data.json", "r"))
    #     changelogs_json = json.load(open("tests/unit_test/data/changelogs_data.json", "r"))

    #     mock_get_versions.return_value = self.versions_data

    #     # execute
    #     transformed_changelogs = self.jira_exporter.transform_changelogs(self.changelogs_data)
    #     transformed_changelogs_json = self.jira_exporter.dataframe_to_json(transformed_changelogs)

    #     # assert
    #     self.assertListEqual(transformed_changelogs_json,status_change_json)