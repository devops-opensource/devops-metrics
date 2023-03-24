import pytest
from unittest.mock import MagicMock, patch
from src.loader import loader
from src.loader.splunk_loader import SplunkLoader
from splunk_http_event_collector import http_event_collector
import pandas as pd


@pytest.fixture
def sample_config():
    return {
        "SPLUNK": {
            "splunk_url": "https://splunk.example.com",
            "splunk_key": "your_splunk_key",
            "splunk_index": "your_splunk_index",
        }
    }

@pytest.fixture
def sample_df_status_changes():
    data = [
        {
            "key": "TEST-1",
            "from_status": "Open",
            "to_status": "In Progress",
            "to_date": "2023-03-01",
            "creation_date": "2023-02-20",
            "version": "Example Version 1",
        },
        {
            "key": "TEST-2",
            "from_status": "In Progress",
            "to_status": "Resolved",
            "to_date": "2023-03-10",
            "creation_date": "2023-02-25",
            "version": "Example Version 2",
        },
    ]
    return pd.DataFrame(data)

@pytest.fixture
def sample_df_versions():
    data = [
        {
            "name": "Example Version 1",
            "release_date": pd.to_datetime("2023-03-05"),
            "start_date": pd.to_datetime("2023-02-01"),
            "released": True,
        },
        {
            "name": "Example Version 2",
            "release_date":  pd.to_datetime("2023-03-15"),
            "start_date":  pd.to_datetime("2023-02-15"),
            "released": True,
        },
    ]
    return pd.DataFrame(data)


@pytest.fixture
def sample_df_dict(sample_df_versions,sample_df_status_changes):
    return {"release_management": sample_df_versions,
            "status_changes": sample_df_status_changes }

def test_initialize_data(sample_config):
    splunk_loader = SplunkLoader()
    splunk_loader.initialize_data(sample_config)

    assert splunk_loader._splunk_url == sample_config["SPLUNK"]["splunk_url"]
    assert splunk_loader._splunk_key == sample_config["SPLUNK"]["splunk_key"]
    assert splunk_loader._splunk_index == sample_config["SPLUNK"]["splunk_index"]


# @patch("src.loader.splunk_http_event_collector.http_event_collector", autospec=True)
# def test_load_data(mock_http_event_collector, sample_config, sample_df_dict):
#     mock_http_event_collector_instance = MagicMock(spec=http_event_collector)
#     mock_http_event_collector.return_value = mock_http_event_collector_instance

#     splunk_loader = SplunkLoader()
#     splunk_loader.initialize_data(sample_config)
#     splunk_loader.load_data(sample_df_dict)

#     mock_http_event_collector.assert_called_with(
#         sample_config["SPLUNK"]["splunk_key"],
#         sample_config["SPLUNK"]["splunk_url"]
#     )


# @patch("src.loader.splunk_http_event_collector.http")
# def test_load_data_with_last_update(mock_http_event_collector, sample_config, sample_df_dict):
#     mock_load_data = MagicMock()

#     splunk_loader = SplunkLoader()
#     splunk_loader.load_data = mock_load_data
#     splunk_loader.initialize_data(sample_config)
#     splunk_loader.load_data_with_last_update(sample_df_dict)

#     mock_load_data.assert_called_with(sample_df_dict)