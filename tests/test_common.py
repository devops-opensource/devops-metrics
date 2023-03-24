import pytest
from src.extractor.jiracloud_exporter import  JiracloudExporter
from src.loader.csv_loader import CsvLoader
from src.loader.mysql_loader import MySqlLoader
import pandas as pd

# Import the functions from your provided code
from src.common import common


def test_execution_time():
    @common.execution_time
    def test_function(a, b):
        return a + b

    result = test_function(1, 2)
    assert result == 3


def test_ExporterFactory():
    jira_cloud = common.ExporterFactory("JiraCloud")
    assert isinstance(jira_cloud, JiracloudExporter)


def test_LoaderFactory():
    mysql = common.LoaderFactory("MYSQL")
    csv = common.LoaderFactory("CSV")

    assert isinstance(mysql, MySqlLoader)
    assert isinstance(csv, CsvLoader)


@pytest.fixture
def sample_df():
    data = {
        "column1": [1, 2, 3],
        "column2": ["2021-01-01", "2021-01-02", "2021-01-03"]
    }
    return pd.DataFrame(data)


def test_convert_column_to_datetime(sample_df):
    result_df = common.convert_column_to_datetime("column2", sample_df)

    assert result_df["column2"].dtype == "<M8[ns]"


def test_convert_column_to_datetime_nonexistent_column(sample_df):
    result_df = common.convert_column_to_datetime("nonexistent_column", sample_df)
    
    assert "nonexistent_column" in result_df.columns
    assert all(pd.isna(result_df["nonexistent_column"]))