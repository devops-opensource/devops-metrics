import sys,getopt
import requests
import json
import configparser

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
        response = requests.put(elk_url+"/"+index_name,headers=headers,data=json.dumps(mapping))
        return response

def main(argv):
    """
    This script create a new index and post the jira logs in an elk instance
    """
    index_name = None
    try:
        opts, args = getopt.getopt(argv,"i:",["index="])
    except getopt.GetoptError:
        print("jirascript.py -i <indexname>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--index"):
            index_name = arg
    
    config = configparser.ConfigParser()
    config.read('config.cfg')
    response = elk_create_new_index(index_name,config)

if __name__ == "__main__":
    main(sys.argv[1:])
