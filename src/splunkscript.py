from splunk_http_event_collector import http_event_collector


def export_log(logs, config):
    splunk_url = config["SPLUNK"]["splunk_url"]
    splunk_key = config["SPLUNK"]["splunk_key"]
    splunk_index = config["SPLUNK"]["splunk_index"]

    logsevent = http_event_collector(splunk_key, splunk_url)
    payload = {}
    payload.update({"index": splunk_index})
    payload.update({"sourcetype": "metric"})

    for log in logs:
        payload.update({"event": log})
        logsevent.batchEvent(payload)
    logsevent.flushBatch()
