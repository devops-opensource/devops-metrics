from splunk_http_event_collector import http_event_collector
from src.loader import loader

class SplunkLoader(loader.Loader):
    def initialize_data(self,config):
        self._splunk_url = config["SPLUNK"]["splunk_url"]
        self._splunk_key = config["SPLUNK"]["splunk_key"]
        self._splunk_index = config["SPLUNK"]["splunk_index"]

    def load_data(self,df_dict):
        logsevent = http_event_collector(self._splunk_key, self._splunk_url)
        payload = {}
        payload.update({"index": self._splunk_index})
        payload.update({"sourcetype": "metric"})

        for df in df_dict.values():
            logs = df.to_json(orient="records")
            payload.update({"event": logs})
            logsevent.batchEvent(payload) 
        logsevent.flushBatch()
        
    def load_data_with_last_update(self,df_dict):
        # TODO: Add call to splunk API to get the last update time
        return self.load_data(df_dict)
