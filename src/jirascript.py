import requests
import math
import csv
import json
import pandas 

class JiraExporter:

    def __init__(self,config, jira_type, epic_key):
        if(jira_type == "server"):
            self.email = config["JIRA_SERVER"]["jira_user_email"]
            self.passwd = config["JIRA_SERVER"]["jira_user_password"]
            self.jira_adress = config["JIRA_SERVER"]["jira_server_url"]
            
        else:
            self.email = config["JIRA_CLOUD"]["jira_user_email"]
            self.passwd = config["JIRA_CLOUD"]["jira_user_token"]
            self.jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self.epic_link_field = "customfield_11200"
        self.headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        }
        self.project_key = config["JIRA_SERVER"]["jira_project_key"]
        self.epic_key = epic_key
        self.project_id =  -1
        self.new_status_dict = dict()
        self.df_logs = pandas.DataFrame()


    def get_changelogs(self):
        # self.get_test_execution()
        changelogs = self.get_status_change_logs()
        self.df_logs = self.transform_changelogs(changelogs)
        
        self.save_logs_in_json()
        self.save_logs_in_csv()

        return json.loads(self.df_logs.to_json(orient="records"))

    def get_test_execution(self):
            self.get_test_execution()
            # TODO: save as a json and csv

    def execute_jql_request(self, query, fields, parameters):
        jira_search_url = f"{self.jira_adress}/rest/api/2/search?"
        
        field_string = f"&{fields}" if fields else ""
        parameters_string = f"&{parameters}" if parameters else ""
        query_string = f"jql={query}"

        jql_query = f"{jira_search_url}{query_string}{field_string}{parameters_string}"
        response = requests.get(jql_query, auth=(self.email, self.passwd), headers=self.headers)
        
        try: 
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        reponse = self.execute_multiple_pages(response.json(),query, fields, parameters)

        return reponse

    def execute_xray_request(self, endpoint, parameters):
        jira_url = f"{self.jira_adress}/rest/raven/2.0/api/{endpoint}"
        

        parameters_string = f"?{parameters}" if parameters else ""

        query = f"{jira_url}{parameters_string}"
        response = requests.get(query, auth=(self.email, self.passwd), headers=self.headers)
        
        try: 
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        return response.json()

    def execute_multiple_pages(self,json_output, query, fields, parameters):
        max_results = json_output["maxResults"]
        nb_of_pages = math.ceil(json_output["total"]/max_results)
        print("max results: " + str(max_results) + " json total: " + str(json_output["total"]))
        result = json_output["issues"]

        for i in range(1, nb_of_pages):
                print(str(i)+"/"+str(nb_of_pages))
                parameters =f"{parameters}&startAt={str(i*max_results)}"
                response = self.execute_jql_request(query, fields, parameters)
                result.extend(response["issues"])
        return result
    
    def get_test_execution(self):
        """
        Get ticket changelogs from a jira + xray server
        """
        # 1) Retrieve the test executions
        fields = f""
        parameters = "maxResults=200"
        query = f"project = {self.project_key} AND issuetype = 'Test Execution' AND createdDate > startOfMonth()"

        json = self.execute_jql_request(query, fields, parameters)
        # 2) Retrieve the execution for those tests 
        executions = [] 

        for execution in json: 
            parameters = f"testExecKey={execution['key']}"
            endpoint = f"testruns"
            response = self.execute_xray_request(endpoint, parameters)       
            if len(response) > 0:
                for execution_info in response: 
                    test_execution_model = {
                        "event_type": "test_execution",
                        "key": execution_info['testExecKey'],
                        "test_key": execution_info['testKey'],
                        "project_key": self.project_key,
                        "status": execution_info['status'],
                        "test_type": execution_info["type"] if "type" in execution_info else "", 
                        "started_at": execution_info["start"] if "start" in execution_info else "",
                        "ended_at":  execution_info["finish"] if "finish" in execution_info else "",
                        "executed_by": execution_info["executedBy"] if "executedBy" in execution_info else "",
                        "environment": execution_info["testEnvironments"][0] if len(execution_info["testEnvironments"]) == 1 else ""
                    }
                    executions.append(test_execution_model)
            else:
                print(json)         
        # 3)

        return executions

    def get_status_change_logs(self):
        """
        Get ticket changelogs from a jira server
        """
        fields = f"issuetype,status,created,project,parent,{self.epic_link_field}"
        parameters = "expand=changelog&maxResults=200"
        query = f"cf[11200]= {self.epic_key}" if self.epic_key else f"project={self.project_key}"

        changelogs = self.execute_jql_request(query, fields, parameters)

        return changelogs

    def transform_changelogs(self,changelogs):
        
        fields_to_keep = ["key","fields.project.key","fields.customfield_11200",
            "fields.issuetype.name","changelog.histories.created","fromString","toString","from_date"]
        
        fieldnames_mapping = {"key":"key",
                            "fields.project.key":"project_key",
                            "fields.customfield_11200":"parent_key",
                            "fields.issuetype.name":"issue_type",
                            "fromString":"from_status",
                            "toString":"to_status",
                            "changelog.histories.created":"to_date"}

        norm_history = pandas.json_normalize(changelogs,["changelog","histories","items"],["key",["changelog","histories","created"]])
        norm_fields = pandas.json_normalize(changelogs)
        norm_merged = norm_history.merge(norm_fields)
        
        norm_merged = norm_merged[norm_merged["field"]=="status"]
        norm_merged["changelog.histories.created"] = pandas.to_datetime(norm_merged["changelog.histories.created"])
        norm_merged["fields.created"] = pandas.to_datetime(norm_merged["fields.created"])
        norm_merged["from_date"] = norm_merged.sort_values(["changelog.histories.created"]).groupby("key")["changelog.histories.created"].shift()
        norm_merged["from_date"].fillna(norm_merged["fields.created"],inplace=True)
        for col in norm_merged.columns:
            if col not in fields_to_keep:
                norm_merged = norm_merged.drop(columns=col)
        
        norm_merged = norm_merged.rename(columns=fieldnames_mapping)

        return norm_merged


    def save_logs_in_csv(self):
        """
        Save a list of Jira logs as a csv file
        """
        with open("data.csv", 'w', encoding="UTF-8", newline='') as file:
            self.df_logs.to_csv(file)
        # fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
        # with open("data.csv", 'w', encoding="UTF-8", newline='') as file:
        #     write = csv.writer(file)
        #     write.writerow(fields)
        #     for log in self.log_list:
        #         write.writerow(log.values())

    def save_logs_in_json(self):
        """
        Save a list of Jira logs as a json file
        """       
        with open("data.json",'w',encoding="UTF=8") as file:
            self.df_logs.to_json(file,orient="records")
            #json.dump(self.log_list,file)
#TODO
"""
Un potentiel problème est si l'historique de changement comporte plus de 100 entrées. Si cela devient une
limitation il faudra alors faire un appel sur GET /rest/api/3/issue/{issueIdOrKey}/changelog

Pour rendre les champs que l'on récupère totalement paramétrables, créer une fonction récursive qui explore
les champs et les dictionnaires retournés: exemple si le chemin d'un champs est /fields/trucA/trucB alors il faudra
un premier appel pour récupérer le dict fields, un autre pour récupérer le dict trucA et enfin un appel terminal pour accéder
champ truc

Pour réduire le temps d'exécution on pourrait modifier les requêtes pour ne retourner que les champs nécessaires, cela réduirait
le payload des réponses
"""
