import pytest
from unittest.mock import Mock, MagicMock
from unittest.mock import patch
import pandas as pd

from src.extractor.jiracloud_exporter import JiracloudExporter

@pytest.fixture
def mock_config():
    return {
        "JIRA_CLOUD": {
            "jira_user_email": "user@example.com",
            "jira_token": "token",
            "jira_cloud_url": "https://jira.example.com",
            "jira_project_keys": "PROJECT",
            "jira_creation_status": "Created",
            "jira_released_status": "Released",
            "jira_closed_statuses": "Closed,Resolved"
        }
    }

@pytest.fixture
def jira_cloud_config():
    config = {
        "JIRA_CLOUD": {
            "jira_user_email": "test@example.com",
            "jira_token": "test_token",
            "jira_cloud_url": "https://test.atlassian.net",
            "jira_project_keys": "TEST",
            "jira_creation_status": "Created",
            "jira_released_status": "Released",
            "jira_closed_statuses": "Closed,Done"
        }
    }
    return config

@pytest.fixture
def mock_exporter():
    config = {
        "JIRA_CLOUD": {
            "jira_user_email": "user@example.com",
            "jira_token": "jira_token",
            "jira_cloud_url": "https://example.com",
            "jira_project_keys": "EXAMPLE",
        }
    }

    exporter = JiracloudExporter()
    exporter.initialize_data(config)
    return exporter

def test_init(jira_cloud_config):
    jira_cloud = JiracloudExporter()
    jira_cloud.initialize_data(jira_cloud_config)
    assert jira_cloud._email == jira_cloud_config["JIRA_CLOUD"]["jira_user_email"]
    assert jira_cloud._token == jira_cloud_config["JIRA_CLOUD"]["jira_token"]
    assert jira_cloud._jira_adress == jira_cloud_config["JIRA_CLOUD"]["jira_cloud_url"]
    assert jira_cloud._project_keys == jira_cloud_config["JIRA_CLOUD"]["jira_project_keys"]

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

def test_create_session(mock_exporter):
    session = mock_exporter.create_session()
    assert session.auth == (mock_exporter._email, mock_exporter._token)
    assert session.headers["Accept"] == "application/json"
    assert session.headers["Content-Type"] == "application/json"

def test_execute_project_version_request(mock_exporter):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "values": [],
        "total": 0,
        "maxResults": 50
    }
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_exporter.create_session = MagicMock(return_value=mock_session)

    parameters = ""
    response = mock_exporter.execute_project_version_request(parameters)

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
@pytest.fixture
def sample_changelogs_multiple_pages():
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


@pytest.fixture
def mock_response_version():
    response = MagicMock()
    response.json.return_value = {
        "values": [],
        "total": 0,
        "maxResults": 50,
    }
    response.raise_for_status.return_value = None
    return response

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.json.return_value = {
        "issues": [],
        "total": 0,
        "maxResults": 50,
    }
    response.raise_for_status.return_value = None
    return response

def test_execute_project_version_request(mock_exporter, mock_response_version):
    with patch("requests.Session.get", return_value=mock_response_version):
        result = mock_exporter.execute_project_version_request(
            "EXAMPLE", "", is_recursive=False
        )
    assert isinstance(result, list)

def test_execute_jql_request(mock_exporter, mock_response):
    with patch("requests.Session.get", return_value=mock_response):
        result = mock_exporter.execute_jql_request(
            "query", "fields", "", is_recursive=False
        )
    assert isinstance(result, list)

def test_execute_jql_request_multiple_pages(mock_exporter):
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = {
        "issues": [],
        "total": 100,
        "maxResults": 50,
        "startAt": 0,
    }
    mock_response_page1.raise_for_status.return_value = None

    mock_response_page2 = MagicMock()
    mock_response_page2.json.return_value = {
        "issues": [],
        "total": 100,
        "maxResults": 50,
        "startAt": 50,
    }
    mock_response_page2.raise_for_status.return_value = None

    with patch("requests.Session.get", side_effect=[mock_response_page1, mock_response_page2]):
        result = mock_exporter.execute_jql_request(
            "query", "fields", "", is_recursive=False
        )

    assert isinstance(result, list)


def test_extract_data(mock_exporter):
    with patch.object(mock_exporter, "extract_project_versions") as mock_extract_project_versions, \
        patch.object(mock_exporter, "extract_status_changelogs") as mock_extract_status_changelogs:

        mock_extract_project_versions.return_value = {"EXAMPLE": []}
        mock_extract_status_changelogs.return_value = []

        result = mock_exporter.extract_data()

    assert isinstance(result, dict)
    assert set(result.keys()) == {"versions", "status_changes"}

def test_adapt_data(mock_exporter):
    with patch.object(mock_exporter, "adapt_versions") as mock_adapt_versions, \
        patch.object(mock_exporter, "adapt_status_changes") as mock_adapt_status_changes:

        mock_adapt_versions.return_value = pd.DataFrame()
        mock_adapt_status_changes.return_value = pd.DataFrame()

        data_dict = {
            "versions": [],
            "status_changes": [],
        }
        result = mock_exporter.adapt_data(data_dict)

    assert isinstance(result, dict)
    assert set(result.keys()) == {"versions", "status_changes"}