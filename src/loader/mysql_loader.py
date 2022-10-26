import pandas as pd
import sqlalchemy

class MySqlLoader:
    def __init__(self, config, password):
        self._host = config["SQL"]["mysql_hostname"]
        self._engine = config["SQL"]["mysql_engine"]
        self._database = config["SQL"]["mysql_database"]
        self._username = config["SQL"]["mysql_username"]
        self._password = password

        # User, pw, and db are being imported from dbconfig.py file to mask credentials
        db_data = ("{engine}://{user}:{pw}@{host}/{db}".format(host=self._host, engine=self._engine, user=self._username, pw=self._password, db=self._database))
        # Using 'create_engine' from sqlalchemy to make the db connection
        self._engine = sqlalchemy.create_engine(db_data).connect()

    def loadReleasesFromDf(self, df):
        dtype = {"release_date": sqlalchemy.DateTime, "start_date": sqlalchemy.DateTime, "control_date": sqlalchemy.DateTime}
        df.to_sql(name='releases', con=self._engine, if_exists='replace', index=False, dtype=dtype)

    def loadStatusChangesFromDf(self, df):
        dtype = {"to_date": sqlalchemy.DateTime, "from_date": sqlalchemy.DateTime, "control_date": sqlalchemy.DateTime}
        df.to_sql(name='status_changes', con=self._engine, if_exists='replace', index=False, dtype=dtype)