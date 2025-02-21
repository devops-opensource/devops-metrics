import pandas as pd
from src.loader import loader
import os

class CsvLoader(loader.Loader):
    def initialize_data(self, config):
        self._prefix = config["CSV"]["csv_filename_prefix"]

    def load_data(self, df_dict, unique_fields_dict=None):
        """
        Load DataFrames to CSV files with optional duplicate prevention per DataFrame type.
        
        Args:
            df_dict (dict): Dictionary of DataFrames where key is the type and value is the DataFrame
            unique_fields_dict (dict, optional): Dictionary mapping DataFrame types to their unique field lists
                Example: {'metrics': ['date', 'model'], 'users': ['user_id']}
        """
        for type, df in df_dict.items():
            csv_name = f"{self._prefix}_{type}.csv"
            unique_fields = unique_fields_dict.get(type) if unique_fields_dict else None
            
            # If file exists and unique_fields are specified for this type, handle duplicates
            if os.path.exists(csv_name) and unique_fields:
                existing_df = pd.read_csv(csv_name)
                
                # Ensure all unique_fields exist in both dataframes
                if not all(field in df.columns for field in unique_fields) or \
                   not all(field in existing_df.columns for field in unique_fields):
                    raise ValueError(f"Some unique fields {unique_fields} not found in dataframes for type {type}")
                
                # Identify and remove duplicates based on unique_fields
                merged_df = pd.concat([existing_df, df])
                merged_df = merged_df.drop_duplicates(subset=unique_fields, keep='last')
                
                # Save the merged dataframe
                merged_df.to_csv(csv_name, index=False)
                print(f"CSV file {csv_name} updated with new unique records")
            else:
                # If file doesn't exist or no unique_fields specified, write/overwrite the file
                df.to_csv(csv_name, index=False)
                print(f"CSV file {csv_name} created")