import pytest
import pandas as pd
import numpy as np
from src.transformer.copilot_transformer import CopilotTransformer

@pytest.fixture
def mock_config():
    return {
        "GITHUB_COPILOT": {
            "some_config": "value"
        }
    }

@pytest.fixture
def transformer():
    transformer = CopilotTransformer()
    transformer.initialize_data({})
    return transformer

@pytest.fixture
def sample_chat_metrics_team():
    return pd.DataFrame({
        'team': ['team1', 'team1', 'team2'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-01'],
        'total_chat': [100, 200, 150],
        'total_engaged_users': [10, 20, 15],
        'total_chat_copy_events': [30, 60, 45],
        'total_chat_insertion_events': [20, 40, 30]
    })

@pytest.fixture
def sample_chat_metrics_global():
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'total_chat': [250, 200],
        'total_engaged_users': [25, 20],
        'total_chat_copy_events': [75, 60],
        'total_chat_insertion_events': [50, 40]
    })

@pytest.fixture
def sample_completion_metrics_team():
    return pd.DataFrame({
        'team': ['team1', 'team1', 'team2'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-01'],
        'language': ['python', 'python', 'javascript'],
        'total_code_lines_accepted': [500, 600, 450],
        'total_code_lines_suggested': [1000, 1200, 900]
    })

@pytest.fixture
def sample_completion_metrics_global():
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'language': ['python', 'javascript'],
        'total_code_lines_accepted': [950, 450],
        'total_code_lines_suggested': [2000, 900]
    })

@pytest.fixture
def sample_daily_active_users():
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'active_users': [100, 200, 300]
    })

def test_initialize_data(transformer, mock_config):
    transformer.initialize_data(mock_config)
    assert transformer.config == mock_config

def test_sanitize_metrics(transformer):
    df = pd.DataFrame({
        'col1': [float('inf'), float('-inf'), np.nan, 1.0],
        'col2': [1.0, np.nan, float('inf'), 2.0]
    })
    
    result = transformer.sanitize_metrics(df)
    
    assert not result.isin([float('inf'), float('-inf')]).any().any()
    assert not result.isna().any().any()
    assert (result[result['col1'] == 0].shape[0] == 3)  # Three values replaced: inf, -inf, and nan
    assert (result[result['col2'] == 0].shape[0] == 2)  # One inf and one nan replaced

def test_transform_average_active_users(transformer, sample_daily_active_users):
    result = transformer.transform_average_active_users(sample_daily_active_users)
    
    assert isinstance(result, pd.DataFrame)
    assert 'average_active_users' in result.columns
    assert result['average_active_users'].iloc[0] == 200  # (100 + 200 + 300) / 3

def test_transform_chat_metrics_team(transformer, sample_chat_metrics_team):
    result = transformer.transform_chat_metrics_team(sample_chat_metrics_team)
    
    assert isinstance(result, pd.DataFrame)
    assert set(['team', 'date', 'chat_per_user', 'chat_acceptance_rate']).issubset(result.columns)
    
    # Test calculations for team1's first day
    team1_day1 = result[(result['team'] == 'team1') & (result['date'] == '2024-01-01')].iloc[0]
    assert team1_day1['chat_per_user'] == pytest.approx(10.0)  # 100/10
    assert team1_day1['chat_acceptance_rate'] == pytest.approx(0.5)  # (30+20)/100

def test_transform_chat_metrics_global(transformer, sample_chat_metrics_global):
    result = transformer.transform_chat_metrics_global(sample_chat_metrics_global)
    
    assert isinstance(result, pd.DataFrame)
    assert set(['date', 'chat_per_user', 'chat_acceptance_rate']).issubset(result.columns)
    
    # Test calculations for first day
    day1 = result[result['date'] == '2024-01-01'].iloc[0]
    assert day1['chat_per_user'] == pytest.approx(10.0)  # 250/25
    assert day1['chat_acceptance_rate'] == pytest.approx(0.5)  # (75+50)/250

def test_transform_completion_metrics_team(transformer, sample_completion_metrics_team):
    result = transformer.transform_completion_metrics_team(sample_completion_metrics_team)
    
    assert isinstance(result, pd.DataFrame)
    assert set(['team', 'date', 'language', 'completion_acceptance_rate']).issubset(result.columns)
    
    # Test calculations for team1's first day
    team1_day1 = result[(result['team'] == 'team1') & 
                        (result['date'] == '2024-01-01') & 
                        (result['language'] == 'python')].iloc[0]
    assert team1_day1['completion_acceptance_rate'] == pytest.approx(0.5)  # 500/1000

def test_transform_completion_metrics_global(transformer, sample_completion_metrics_global):
    result = transformer.transform_completion_metrics_global(sample_completion_metrics_global)
    
    assert isinstance(result, pd.DataFrame)
    assert set(['date', 'language', 'completion_acceptance_rate']).issubset(result.columns)
    
    # Test calculations for python
    python_metrics = result[result['language'] == 'python'].iloc[0]
    assert python_metrics['completion_acceptance_rate'] == pytest.approx(0.475)  # 950/2000

def test_transform_data_complete_workflow(transformer):
    adapted_data = {
        'df_metrics_chat_team': pd.DataFrame({
            'team': ['team1'],
            'date': ['2024-01-01'],
            'total_chat': [100],
            'total_engaged_users': [10],
            'total_chat_copy_events': [30],
            'total_chat_insertion_events': [20]
        }),
        'df_metrics_completion_team': pd.DataFrame({
            'team': ['team1'],
            'date': ['2024-01-01'],
            'language': ['python'],
            'total_code_lines_accepted': [500],
            'total_code_lines_suggested': [1000]
        })
    }
    
    result = transformer.transform_data(adapted_data)
    
    assert isinstance(result, dict)
    assert 'df_metrics_chat_team' in result
    assert 'df_metrics_completion_team' in result

def test_transform_data_with_invalid_data(transformer):
    adapted_data = {
        'df_metrics_chat_team': pd.DataFrame({
            'team': ['team1', 'team1'],
            'date': ['2024-01-01', '2024-01-01'],
            'total_chat': [float('inf'), 100],
            'total_engaged_users': [10, np.nan],
            'total_chat_copy_events': [30, float('-inf')],
            'total_chat_insertion_events': [20, 20]
        })
    }
    
    result = transformer.transform_data(adapted_data)
    
    assert isinstance(result, dict)
    assert 'df_metrics_chat_team' in result
    df_result = result['df_metrics_chat_team']
    assert not df_result.isin([float('inf'), float('-inf')]).any().any()
    assert not df_result.isna().any().any()
    # Verify that the sanitized values were used in calculations
    assert df_result['chat_per_user'].iloc[0] == pytest.approx(0.0)  # inf/10 -> 0/10 = 0
    assert df_result['chat_acceptance_rate'].iloc[0] == pytest.approx(0.0)  # (30+20)/0 -> 0
