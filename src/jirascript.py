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
        self.log_list = list()


    def run(self):
        self.project_id = self.get_project_id()
        self.new_status_dict = self.get_new_statuses()
        changelogs = self.get_status_change_logs()
        self.log_list = self.transform_changelogs(changelogs)
        
        self.save_logs_in_json()
        self.save_logs_in_csv()

        return self.log_list

    def execute_jql_request(self,query,fields,parameters):
        jira_search_url = f"{self.jira_adress}/searchrest/api/2/search?"
        
        field_string = f"&{fields}" if fields else ""
        parameters_string = f"&{parameters}" if parameters else ""
        query_string = f"jql={query}"

        jql_query = f"{jira_search_url}{query}{field_string}{parameters_string}"
        response = requests.get(jql_query, auth=(self.email, self.passwd), headers=self.headers)
        
        try: 
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        return response.json()

    def get_status_change_logs(self):
        """
        Get ticket changelogs from a jira server
        """
        jira_fields = f"issuetype,status,created,project,parent,{self.epic_link_field}"
        jira_others = "expand=changelog&maxResults=200"
        jira_jql = f"cf[11200]= {self.epic_key}" if self.epic_key else f"project={self.project_key} AND issuetype in (Story)"

        json = execute_jql_request(jira_jql, fields, parameters)
      
        max_results = json["maxResults"]
        nb_of_pages = math.ceil(json["total"]/max_results)
        print("max results: " + str(max_results) + " json total: " + str(json["total"]))
        changelogs= response.json()["issues"]

        for i in range(0, nb_of_pages):
            if(i>0):
                print(str(i)+"/"+str(nb_of_pages))
                response = requests.get(jira_search_url+jira_jql+jira_fields+jira_others+"&startAt="+str(i*max_results),
                    auth=(self.email, self.passwd), headers=self.headers)
                changelogs.extend(response.json()["issues"])

        return changelogs

    def transform_changelogs(self,changelogs):
        
        fields_to_keep = ["key","fields.project.key","fields.customfield_11200","fields.status.name",
            "fields.issuetype.name","changelog.histories.created","field","toString"]
        
        norm_history = pandas.json_normalize(changelogs,["changelog","histories","items"],["key",["changelog","histories","created"]])
        norm_fields = pandas.json_normalize(changelogs)
        norm_merged = norm_history.merge(norm_fields)
        norm_merged = norm_merged.append(norm_merged.drop_duplicates("key")
            .assign(field="status",toString=lambda x:x["fields.issuetype.id"]), ignore_index=True)

        for col in norm_merged.columns:
            if col not in fields_to_keep:
                norm_merged = norm_merged.drop(columns=col)
        print(norm_merged)


        log_list = []
        for issue in changelogs:
            issuetype_id = issue["fields"]["issuetype"]["id"]
            new_status_tuple = self.new_status_dict[issuetype_id]
            log = self.create_log(issue, issue["fields"]["created"], 
                status_id = new_status_tuple[0], status_name = new_status_tuple[1])
            log_list.append(log)
            for changelog in issue["changelog"]["histories"]:
                for item in changelog["items"]:
                    if(item["field"]=="status"):
                        log = self.create_log(issue,changelog["created"],item["to"],item["toString"])
                        log_list.append(log)

        return log_list

    def create_log(self,issue, timestamp, status_id, status_name):
        """
        Create a log entry
        issue["fields"]["created"], issue["id"],issue["key"],issue["project"]["id"], issue["project"]["key"]
        """
        log = dict()
        epic_link_field = "customfield_11200"
        log["timestamp"] = timestamp
        log["id"] = int(issue["id"])
        log["key"] = issue["key"]
        log["project_id"] = int(issue["fields"]["project"]["id"])
        log["project_key"] = issue["fields"]["project"]["key"]
        if(issue["fields"].get("parent") is not None):
            log["parent_id"] = int(issue["fields"]["parent"]["id"])
            log["parent_key"] = issue["fields"]["parent"]["key"]
        elif(issue["fields"].get(epic_link_field) is not None):
            log["parent_key"] = issue["fields"][epic_link_field]
            log["parent_id"] = -1
        else:
            log["parent_id"] = -1
            log["parent_key"] = "null"
        log["type_id"] = int(issue["fields"]["issuetype"]["id"])
        log["type_name"] = issue["fields"]["issuetype"]["name"]
        log["status_id"] = int(status_id)
        log["status_name"] = status_name
        return log

    def get_project_id(self):
        """
        return the id associated to a project key after getting the project list from the jira instance
        """
        project_list_response = requests.get(self.jira_adress+"/rest/api/2/project",auth=(self.email, self.passwd), headers=self.headers)
        if(project_list_response.status_code != 200):
            print(project_list_response.content)
            return #TODO lancer une exception
        
        project_list = project_list_response.json()

        project = list(filter(lambda x: (x["key"] == self.project_key),project_list))

        if(len(project) > 0):
            return project[0]["id"]
        return -1

    def get_new_statuses(self):
        """
        return a dict containing the id and name of the new status for each issue type
        """
        status_list_url = self.jira_adress+"/rest/api/2/project/"+self.project_id+"/statuses"
        status_list_response = requests.get(status_list_url,auth=(self.email, self.passwd), headers=self.headers)
        if(status_list_response.status_code != 200):
            print(status_list_response.content)
            return #TODO lancer une exception

        status_list = status_list_response.json()

        new_status_dict = dict() 
        for ticket in status_list:
            for status in ticket["statuses"]:
                if(status["statusCategory"]["key"]=="new"):
                    new_status_dict[ticket["id"]]=(status["id"],status["name"])
        return new_status_dict

    def save_logs_in_csv(self):
        """
        Save a list of Jira logs as a csv file
        """
        fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
        with open("data.csv", 'w', encoding="UTF-8", newline='') as file:
            write = csv.writer(file)
            write.writerow(fields)
            for log in self.log_list:
                write.writerow(log.values())

    def save_logs_in_json(self):
        """
        Save a list of Jira logs as a json file
        """       
        with open("data.json",'w',encoding="UTF=8") as file:
            json.dump(self.log_list,file)
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