import pytest
from unittest.mock import Mock, MagicMock
from unittest.mock import patch
import pandas as pd
import json
from src.extractor.jiracloud_extractor import JiraCloud

@pytest.fixture
def mock_config():
    return {
        "JIRA_CLOUD": {
            "jira_user_email": "user@example.com",
            "jira_token": "token",
            "jira_cloud_url": "https://jira.example.com",
            "jira_project_key": "PROJECT",
            "jira_creation_status": "Created",
            "jira_released_status": "Released",
            "jira_closed_statuses": "Closed,Resolved"
        }
    }


@pytest.fixture
def jira_cloud(mock_config):
    return JiraCloud(mock_config)

def test_init(jira_cloud_config):
    jira_cloud = JiraCloud(jira_cloud_config)
    assert jira_cloud.email == jira_cloud_config["JIRA_CLOUD"]["jira_user_email"]
    assert jira_cloud.token == jira_cloud_config["JIRA_CLOUD"]["jira_token"]
    assert jira_cloud.jira_adress == jira_cloud_config["JIRA_CLOUD"]["jira_cloud_url"]
    assert jira_cloud.project_key == jira_cloud_config["JIRA_CLOUD"]["jira_project_key"]
    assert jira_cloud.creation_status == jira_cloud_config["JIRA_CLOUD"]["jira_creation_status"]
    assert jira_cloud.released_status == jira_cloud_config["JIRA_CLOUD"]["jira_released_status"]
    assert jira_cloud.closed_statuses == jira_cloud_config["JIRA_CLOUD"]["jira_closed_statuses"].split(",")
    assert isinstance(jira_cloud.df_versions, pd.DataFrame)
    assert isinstance(jira_cloud.df_status_changes, pd.DataFrame)

@pytest.fixture
def jira_cloud_config():
    config = {
        "JIRA_CLOUD": {
            "jira_user_email": "test@example.com",
            "jira_token": "test_token",
            "jira_cloud_url": "https://test.atlassian.net",
            "jira_project_key": "TEST",
            "jira_creation_status": "Created",
            "jira_released_status": "Released",
            "jira_closed_statuses": "Closed,Done"
        }
    }
    return config

@pytest.fixture
def sample_df_status_changes():
    data = {
        "key": ["PROJECT-1"],
        "project_key": ["PROJECT"],
        "parent_key": ["PROJECT-0"],
        "issue_type": ["Story"],
        "from_status": ["Created"],
        "to_status": ["Closed"],
        "to_date": [pd.to_datetime("2021-01-02", utc=True)],
        "from_date": [pd.to_datetime("2021-01-01", utc=True)],
        "version": ["v1.0"],
        "event_type": ["status_change"],
        "control_date": [pd.to_datetime("2021-01-02", utc=True)]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_df_release_management():
    data = {
        "name": ["v1.0"],
        "description": ["Version 1.0"],
        "release_date": [pd.to_datetime("2021-01-03", utc=True)],
        "start_date": [pd.to_datetime("2021-01-01", utc=True)],
        "event_type": ["release_management"],
        "project_key": ["PROJECT"],
        "control_date": [pd.to_datetime("2021-01-03", utc=True)]
    }
    return pd.DataFrame(data)

def test_jira_cloud_init(mock_config, jira_cloud):
    assert jira_cloud.email == mock_config["JIRA_CLOUD"]["jira_user_email"]
    assert jira_cloud.token == mock_config["JIRA_CLOUD"]["jira_token"]
    assert jira_cloud.jira_adress == mock_config["JIRA_CLOUD"]["jira_cloud_url"]
    assert jira_cloud.project_key == mock_config["JIRA_CLOUD"]["jira_project_key"]
    assert jira_cloud.creation_status == mock_config["JIRA_CLOUD"]["jira_creation_status"]
    assert jira_cloud.released_status == mock_config["JIRA_CLOUD"]["jira_released_status"]
    assert jira_cloud.closed_statuses == mock_config["JIRA_CLOUD"]["jira_closed_statuses"].split(",")

def test_create_session(jira_cloud):
    session = jira_cloud.create_session()
    assert session.auth == (jira_cloud.email, jira_cloud.token)
    assert session.headers["Accept"] == "application/json"
    assert session.headers["Content-Type"] == "application/json"

def test_execute_project_version_request(jira_cloud):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "values": [],
        "total": 0,
        "maxResults": 50
    }
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    jira_cloud.create_session = MagicMock(return_value=mock_session)

    parameters = ""
    response = jira_cloud.execute_project_version_request(parameters)

    assert response == []
    mock_session.get.assert_called_once()

@pytest.fixture
def sample_versions():
    return [
        {
            "name": "v1.0",
            "description": "Version 1.0",
            "releaseDate": "2021-01-01T00:00:00.000+0000",
            "startDate": "2020-12-01T00:00:00.000+0000",
            "released": True
        },
        {
            "name": "v1.1",
            "description": "Version 1.1",
            "releaseDate": "2021-02-01T00:00:00.000+0000",
            "startDate": "2021-01-15T00:00:00.000+0000",
            "released": True
        }
    ]

def test_transform_versions(jira_cloud, sample_versions):
    transformed_versions = jira_cloud.transform_versions(sample_versions)
    assert isinstance(transformed_versions, pd.DataFrame)
    assert len(transformed_versions) == 2

    expected_columns = ["name", "description", "release_date", "start_date", "event_type", "project_key", "control_date"]
    for col in expected_columns:
        assert col in transformed_versions.columns

    assert transformed_versions["event_type"].iloc[0] == "release_management"
    assert transformed_versions["project_key"].iloc[0] == jira_cloud.project_key

def test_execute_jql_request(jira_cloud):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "issues": [],
        "total": 0,
        "maxResults": 50
    }
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    jira_cloud.create_session = MagicMock(return_value=mock_session)

    query = "project=PROJECT AND issuetype in (Story)"
    fields = "issuetype,status,created,project,parent,fixVersions"
    parameters = "expand=changelog"
    response = jira_cloud.execute_jql_request(query, fields, parameters)


    assert response == []
    mock_session.get.assert_called_once()

@pytest.fixture
def sample_changelogs():
    return [
        {
            "key": "PROJECT-1",
            "fields": {
                "project": {"key": "PROJECT"},
                "parent": {"key": "PROJECT-0"},
                "issuetype": {"name": "Story"},
                "status": {"name": "Closed"},
                "created": "2021-01-01T00:00:00.000+0000",
                "fixVersions": [{"name": "v1.0"}]
            },
            "changelog": {
                "histories": [
                    {
                        "created": "2021-01-02T00:00:00.000+0000",
                        "items": [
                            {
                                "field": "status",
                                "fromString": "Created",
                                "toString": "Closed"
                            }
                        ]
                    }
                ]
            }
        }
    ]

def test_transform_status_changelogs(jira_cloud, sample_changelogs, sample_df_release_management, monkeypatch):
    def mock_get_release_management(self):
        return sample_df_release_management

    monkeypatch.setattr(JiraCloud, "get_release_management", mock_get_release_management)
    
    transformed_changelogs = jira_cloud.transform_status_changelogs(sample_changelogs)
    assert isinstance(transformed_changelogs, pd.DataFrame)
    assert len(transformed_changelogs) == 2

    expected_columns = ["key", "project_key", "parent_key", "issue_type", "from_status", "to_status", "to_date", "from_date", "version", "event_type", "control_date"]
    for col in expected_columns:
        assert col in transformed_changelogs.columns

    assert transformed_changelogs["event_type"].iloc[0] == "status_change"
    assert transformed_changelogs["project_key"].iloc[0] == jira_cloud.project_key



def test_add_transition_to_released_status(jira_cloud, sample_df_status_changes,sample_df_release_management):
    jira_cloud.get_release_management = Mock(return_value=sample_df_release_management)
    df_status_changes = jira_cloud.add_transition_to_released_status(sample_df_status_changes)
    assert isinstance(df_status_changes, pd.DataFrame)
    assert len(df_status_changes) >= len(sample_df_status_changes)

    expected_columns = ["key", "project_key", "parent_key", "issue_type", "from_status", "to_status", "to_date", "from_date", "version", "event_type", "control_date"]
    for col in expected_columns:
        assert col in df_status_changes.columns

    assert (df_status_changes["to_status"] == jira_cloud.released_status).any()



def test_df_drop_columns(jira_cloud):
    data = {
        "key": ["PROJECT-1"],
        "project_key": ["PROJECT"],
        "parent_key": ["PROJECT-0"],
        "issue_type": ["Story"],
        "from_status": ["Created"],
        "to_status": ["Closed"],
        "to_date": [pd.to_datetime("2021-01-02", utc=True)],
        "from_date": [pd.to_datetime("2021-01-01", utc=True)],
        "version": ["v1.0"],
        "event_type": ["status_change"],
        "control_date": [pd.to_datetime("2021-01-02", utc=True)],
        "extra_column": [1]
    }
    df = pd.DataFrame(data)
    columns_to_keep = ["key", "project_key", "parent_key", "issue_type", "from_status", "to_status", "to_date", "from_date", "version", "event_type", "control_date"]

    df_result = jira_cloud.df_drop_columns(df, columns_to_keep)

    assert isinstance(df_result, pd.DataFrame)
    assert len(df_result) == len(df)

    for col in columns_to_keep:
        assert col in df_result.columns

    assert "extra_column" not in df_result.columns