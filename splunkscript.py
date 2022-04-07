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