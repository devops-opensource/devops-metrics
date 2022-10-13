import influxdb_client 
from influxdb_client.client.write_api import SYNCHRONOUS
import json 

bucket = "metrics"
org = "gologic"
token = "abcdef"
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient( url=url, token=token, org=org)

# Write script
write_api = client.write_api(write_options=SYNCHRONOUS)

p = influxdb_client.Point("release").field("name", "GODEVOPS-1.0.0").field("project_key","GODEVOPS").field("release_date", 1644111274).field("start_date","").field("description","blablabla")
write_api.write(bucket=bucket, org=org, record=p)

print("job done")