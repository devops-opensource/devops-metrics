from cmath import log
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
    with open("mapping.json",'r',encoding="UTF-8") as file:
        mapping = json.load(file)
        response = requests.put(elk_url+"/"+index_name,headers=headers,data=json.dumps(mapping))
        return response

def elk_post_logs_bulk(json_file_path,index,config):
    """
    Post in bulk the logs registered in the json_file, in the given index
    """
    elk_url = config["ELK"]["ELASTICSEARCH_URL"]
    headers = {
    "Content-Type": "application/json",
    }
    with open(json_file_path,'r',encoding="UTF-8") as file:
        logs = json.load(file)
        to_insert = "{\"index\":{}}"
        data_string = ""
        for log in logs:
            data_string = data_string + to_insert + "\n" + json.dumps(log) + "\n"
        response = requests.post(elk_url+"/"+index+"/_bulk", headers=headers,data=data_string)
        return response

def main(argv):
    """
    This script create a new index and post the jira logs in an elk instance
    """
    index_name = None
    logfile = None
    try:
        opts, args = getopt.getopt(argv,"i:l:",["index=","logfile="])
    except getopt.GetoptError:
        print("jirascript.py -i <indexname> -l <logfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--index"):
            index_name = arg
        elif opt in ("-l", "--logfile"):
            logfile = arg
    config = configparser.ConfigParser()
    config.read('config.cfg')
    response = elk_create_new_index(index_name,config)
    print(response.content)
    response = elk_post_logs_bulk(logfile,index_name,config)
    print(response.content)

if __name__ == "__main__":
    main(sys.argv[1:])
