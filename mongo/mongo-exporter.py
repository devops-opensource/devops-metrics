import pymongo
import json 

myclient = pymongo.MongoClient("mongodb://localhost:27017/", username='root', password='rootpassword')
dbname = "metrics"
dblist = myclient.list_database_names()
db = myclient[dbname]

db.drop_collection("release")
print("Releases collection dropped !")
releaseColl = db["release"]
with open('releases.json') as file:
    releases = json.load(file)
    releaseColl.insert_many(releases)
print("Insert Releases done !")

db.drop_collection("status_change")
print("Status changes collection dropped !")
scColl= db["status_change"]
with open('status_changes.json') as file:
    status_changes = json.load(file)
    scColl.insert_many(status_changes)
print("Insert Status changes done !")