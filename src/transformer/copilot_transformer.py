from src.transformer.transformer import Transformer
from src.common import common
import pandas as pd

# Currently Copilot data does not need transformation from the dictionaries via which it is extracted
# Placeholder class
# More advanced metrics (efficience plutot que utilisation) will likely require tranformation
class CopilotTransformer(Transformer):
    def initialize_data(self, config):
        self.config = config

    def transform_data(self, adapted_data):
        daily_active_users = adapted_data['df_daily_active_users']
        average_active_users = self.transform_average_active_users(adapted_data['df_daily_active_users'])
        df_seats = adapted_data['df_seats']
        df_dict = {
            "df_daily_active_users": daily_active_users,
            "df_average_active_users": average_active_users,
            "df_seats": df_seats,
        }
        return df_dict
    

    def transform_average_active_users(self, daily_active_users):
        average_active_users = daily_active_users['active_users'].mean().astype(int)
        df = pd.DataFrame({'average_active_users': [average_active_users]})
        return df