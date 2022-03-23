import requests
import json

def elk_create_new_index(index_name,config):
    """
    Create a new index in the elasticsearch instance
    """
    elk_url = config["ELK"]["ELASTICSEARCH_URL"]
    headers = {
    "Content-Type": "application/json",
    }
    with open("mapping.json",'r',encoding="UTF=8") as file:
        mapping = json.load(file)
        response = requests.put(elk_url+"/"+index_name,headers=headers,data=mapping)
        return response