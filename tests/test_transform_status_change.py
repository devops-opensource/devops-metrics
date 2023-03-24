import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.transformer.transform_status_change import TransformStatusChanges

@pytest.fixture
def config():
    return {
        "JIRA_CLOUD": {
            "jira_creation_status": "Open",
            "jira_released_status": "Released",
            "jira_closed_statuses": "Closed,Resolved",
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

def test_transform_status_changes(config, sample_df_status_changes, sample_df_versions):
    transformer = TransformStatusChanges(config, sample_df_versions)
    result = transformer.transform_status_changes(sample_df_status_changes)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert result["event_type"].iloc[0] == "status_change"
    assert isinstance(result["control_date"].iloc[0], pd.Timestamp)

    # Test if the columns are in the correct format
    assert pd.api.types.is_datetime64_ns_dtype(result["from_date"])
    assert pd.api.types.is_datetime64_ns_dtype(result["to_date"])
    assert pd.api.types.is_datetime64_ns_dtype(result["creation_date"])


def test_add_transition_to_released_status(config, sample_df_status_changes, sample_df_versions):
    transformer = TransformStatusChanges(config, sample_df_versions)

    # Modify sample_df_status_changes to simulate closed statuses
    sample_df_status_changes.loc[0, "to_status"] = "Closed"
    sample_df_status_changes.loc[1, "to_status"] = "Resolved"

    result = transformer.add_transition_to_released_status(sample_df_status_changes)

    assert isinstance(result, pd.DataFrame)
    assert len(result) >= 2  # At least two rows for the initial status changes

    # Check if the "Released" status change has been added
    released_status_rows = result[result["to_status"] == config["JIRA_CLOUD"]["jira_released_status"]]
    assert len(released_status_rows) > 0

    # Check if the new "Released" status rows have the correct "release_version" value
    assert "release_version" in released_status_rows.columns
    assert pd.notna(released_status_rows["release_version"]).all()    