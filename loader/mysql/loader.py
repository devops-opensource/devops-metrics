import sqlalchemy
import pandas as pd
from glob import glob

# User, pw, and db are being imported from dbconfig.py file to mask credentials
db_data = ("mysql://{user}:{pw}@{host}/{db}".format(host='localhost:3306', user='gologic', pw='gologic', db='metricsDB'))
# Using 'create_engine' from sqlalchemy to make the db connection
engine = sqlalchemy.create_engine(db_data).connect()
# set the variables for the filepaths of where the source files are and where to move them to
releaseFile = '../../examples/CART_versions.csv'
statusFile = '../../examples/CART_status_changes.csv'

# read file as CSV
df = pd.read_csv(releaseFile)
# print dataframe to the console
print(df)
# insert the dataframe into the db table
dtype = {"release_date": sqlalchemy.DateTime, "start_date": sqlalchemy.DateTime, "control_date": sqlalchemy.DateTime}
df.to_sql(name='releases', con=engine, if_exists='replace', index=False, dtype=dtype)
# print success message to the console
print("release imported!")

# status changes
df = pd.read_csv(statusFile)
dtype = {"to_date": sqlalchemy.DateTime, "from_date": sqlalchemy.DateTime, "control_date": sqlalchemy.DateTime}
df.to_sql(name='status_changes', con=engine, if_exists='replace', index=False, dtype=dtype)
print("status changes imported!")