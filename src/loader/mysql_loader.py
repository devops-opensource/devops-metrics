import pandas as pd
import sqlalchemy

from src.loader import loader


class MySqlLoader(loader.Loader):
    def initialize_data(self, config):
        self._host = config["SQL"]["mysql_hostname"]
        self._engine = config["SQL"]["mysql_engine"]
        self._database = config["SQL"]["mysql_database"]
        self._username = config["SQL"]["mysql_username"]
        self._password = config["SQL"]["mysql_password"]

        # We will add the logic to treat multiple dataframe first        
        db_data = ("{engine}://{user}:{pw}@{host}/{db}".format(host=self._host, engine=self._engine, user=self._username, pw=self._password, db=self._database))
        # Using 'create_engine' from sqlalchemy to make the db connection
        
        # Generate a connection to the database with sqlalchemy to a psotgresql database
        self._engine = sqlalchemy.create_engine(db_data).connect()

    def load_data(self,df_dict):
        for type, df in df_dict.items():
            dtype = self.generate_map_for_alchemysql_datetime_field(df)
            # dtype_test = {"release_date": sqlalchemy.DateTime, "start_date": sqlalchemy.DateTime, "control_date": sqlalchemy.DateTime}
            df.to_sql(name=type, con=self._engine, if_exists='replace', index=False, dtype=dtype)
            print(f"Data loaded in {type} table")
        return []

    def generate_map_for_alchemysql_datetime_field(self, df) -> dict[str, str]:
        """Generate a map for alchemysql datime field"""
        return {col: sqlalchemy.DateTime for col in df.columns if df[col].dtype == "datetime64[ns]"}
        