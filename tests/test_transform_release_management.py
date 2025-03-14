import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.transformer.transform_release_management import TransformReleaseManagement

@pytest.fixture
def sample_df_versions():
    data = [
        {
            "name": "Example Version 1",
            "release_date": "2023-03-01",
            "start_date": "2023-02-20",
            "released": True,
        },
        {
            "name": "Example Version 2",
            "release_date": "2023-03-10",
            "start_date": "2023-03-01",
            "released": True,
        },
        {
            "name": "Example Version 3",
            "release_date": "2023-03-20",
            "start_date": "2023-03-10",
            "released": False,
        },
    ]
    return pd.DataFrame(data)

def test_transform_release_management(sample_df_versions):
    transformer = TransformReleaseManagement()
    result = transformer.transform_release_management(sample_df_versions)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2  # Only 2 released versions

    if "event_type" in result.columns:
        assert result["event_type"].iloc[0] == "release_management"
    
    assert isinstance(result["control_date"].iloc[0], pd.Timestamp)

    # Test if the columns are in the correct format
    assert pd.api.types.is_datetime64_ns_dtype(result["release_date"])
    assert pd.api.types.is_datetime64_ns_dtype(result["start_date"])