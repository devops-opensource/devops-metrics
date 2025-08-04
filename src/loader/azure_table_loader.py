from src.loader import loader
from azure.data.tables import TableServiceClient, TableTransactionError
from uuid import uuid4
import pandas as pd
import hashlib


class AzureTableLoader(loader.Loader):
    def initialize_data(self, config):
        """
        Expected config:
        [AZURE_TABLE]
        connection_string = ...

        [AZURE_TABLES]
        df_billing_seats = BillingSeats
        df_metrics_active_users = ActiveUsers
        ...
        """

        # Read connection string
        azure_table_cfg = config["AZURE_TABLE"]
        self._conn_str = azure_table_cfg.get("connection_string")
        if not self._conn_str:
            raise ValueError("Azure Table connection string not provided")

        # Read DataFrame-to-table mapping from [AZURE_TABLES] section
        if "AZURE_TABLES" in config:
            df_to_table_cfg = dict(config["AZURE_TABLES"])
        else:
            df_to_table_cfg = {}
        self._df_to_table = {k: v for k, v in df_to_table_cfg.items() if k and v}
        if not self._df_to_table:
            raise ValueError("No DataFrame-to-table mappings found in [AZURE_TABLES] section")

        self._table_clients = {}
        service_client = TableServiceClient.from_connection_string(self._conn_str)
        for df_name, table_name in self._df_to_table.items():
            self._table_clients[df_name] = service_client.get_table_client(table_name)

    def _to_entity(self, row: pd.Series, partition_key: str, row_key: str) -> dict:
        """
        Convert a DataFrame row to an Azure Table entity.
        PartitionKey and RowKey are provided as arguments.
        All other columns included as-is.
        """
        entity = row.to_dict()
        entity["PartitionKey"] = partition_key
        entity["RowKey"] = row_key
        return entity

    def _batch_upsert_entities(self, table_client, entities):
        """
        Upsert entities in batches of up to 100.
        All entities in a batch must have the same PartitionKey.
        """
        # Group entities by PartitionKey
        partition_groups = {}
        for entity in entities:
            pk = entity["PartitionKey"]
            if pk not in partition_groups:
                partition_groups[pk] = []
            partition_groups[pk].append(entity)
         
        # Process each partition group
        for partition_key, partition_entities in partition_groups.items():
            # Split into batches of 100
            for i in range(0, len(partition_entities), 100):
                batch = partition_entities[i:i+100]
                operations = [("upsert", entity) for entity in batch]
                try:
                    table_client.submit_transaction(operations)
                except TableTransactionError:
                    # If batch fails, fall back to individual upserts for this batch
                    for entity in batch:
                        table_client.upsert_entity(entity=entity)

    def load_data(self, df_dict: dict):
        """
        Upsert all rows from all DataFrames to their corresponding Azure Table Storage tables.
        For df_billing_seats: use df_name as PartitionKey and concatenation of assignee_login and assignee_id as RowKey.
        For all others: use the dataframe name as PartitionKey and hash of all columns as RowKey.
        Uses mapped Azure Table names from config.
        """

        for df_name, df in df_dict.items():
            # Always use the correct table client for each dataframe
            table_client = self._table_clients.get(df_name)
            if not table_client:
                # Explicitly skip if no table mapping is found
                continue
            
            entities = []
            
            if df_name == "df_billing_seats":
                partition_key = df_name  # Use df_name as partition key
                for _, row in df.copy().iterrows():
                    # Concatenate assignee_login and assignee_id for row key
                    row_key = f"{row['assignee_login']}_{row['assignee_id']}"
                    entity = self._to_entity(row, partition_key, row_key)
                    entities.append(entity)
            else:
                partition_key = df_name
                for _, row in df.copy().iterrows():
                    row_data = row.to_dict()
                    row_data.pop("PartitionKey", None)
                    row_data.pop("RowKey", None)
                    hash_input = "|".join(str(row_data[k]) for k in sorted(row_data.keys()))
                    row_key = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
                    entity = self._to_entity(row, partition_key, row_key)
                    entities.append(entity)
        
            # Batch upsert all entities
            self._batch_upsert_entities(table_client, entities)
