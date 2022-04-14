import sys,getopt,configparser
from splunk_http_event_collector import http_event_collector
import json

def splunk_export_log(index, json_file, config):
    splunk_url = config["SPLUNK"]["splunk_url"]
    splunk_key = config["SPLUNK"]["splunk_key"]
    with open(json_file,'r',encoding="UTF-8") as file:
        logs = json.load(file)
        logsevent = http_event_collector(splunk_key, splunk_url)
        payload = {}
        payload.update({"index":index})
        payload.update({"sourcetype":"metric"})
        for log in logs:
            payload.update({"event":log})
            logsevent.batchEvent(payload)
        logsevent.flushBatch()

def main(argv):
    """
    This script post the jira logs in a splunk index
    """
    index_name = None
    logfile = None
    try:
        opts, args = getopt.getopt(argv,"i:l:",["index=","logfile="])
    except getopt.GetoptError:
        print("splunkscript.py -i <indexname> -l <logfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--index"):
            index_name = arg
        elif opt in ("-l", "--logfile"):
            logfile = arg
    config = configparser.ConfigParser()
    config.read('config.cfg')
    splunk_export_log(index_name,logfile,config)

if __name__ == "__main__":
    main(sys.argv[1:])