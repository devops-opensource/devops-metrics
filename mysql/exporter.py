import os, shutil
from sqlalchemy import create_engine
import pandas as pd
from glob import glob

# User, pw, and db are being imported from dbconfig.py file to mask credentials
db_data = ("mysql://{user}:{pw}@{host}/{db}".format(host='localhost:3306', user='root', pw='rootpassword', db='metricsDB'))
# Using 'create_engine' from sqlalchemy to make the db connection
engine = create_engine(db_data).connect()
# set the variables for the filepaths of where the source files are and where to move them to
releaseFile = '../examples/CART_versions.csv'
statusFile = '../examples/CART_status_changes.csv'

# read file as CSV
df = pd.read_csv(releaseFile)
# print dataframe to the console
print(df)
# insert the dataframe into the db table
df.to_sql(name='releases', con=engine, if_exists='replace', index=False)
# print success message to the console
print("release imported!")

# status changes
df = pd.read_csv(statusFile)
df.to_sql(name='status_changes', con=engine, if_exists='replace', index=False)
print("status changes imported!")