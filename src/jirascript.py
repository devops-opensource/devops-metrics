import sys,getopt
import requests
import math
import csv
import configparser
import json

class JiraExporter:

    def __init__(self,config, jira_type, project_key, epic_key):
        if(jira_type == "server"):
            self.email = config["JIRA_SERVER"]["jira_user_email"]
            self.passwd = config["JIRA_SERVER"]["jira_user_password"]
            self.jira_adress = config["JIRA_SERVER"]["jira_server_url"]
        else:
            self.email = config["JIRA_CLOUD"]["jira_user_email"]
            self.passwd = config["JIRA_CLOUD"]["jira_user_token"]
            self.jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self.headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        }
        self.project_key = project_key
        self.epic_key = epic_key
        self.project_id =  -1
        self.new_status_dict = dict()
        self.log_list = list()

    def run(self):
        self.project_id = self.get_project_id()
        self.new_status_dict = self.get_new_statuses()
        changelogs = self.get_status_change_logs()
        self.log_list = self.transform_changelogs(changelogs)
        return self.log_list

    def get_status_change_logs(self):
        """
        Get ticket changelogs from a jira server
        """
        
        if(self.epic_key == ""):
            response = requests.get(self.jira_adress+"/rest/api/2/search?jql=project="+
                self.project_key+"&fields=issuetype,status,created,project,parent"+
                "&expand=changelog&maxResults=200",auth=(self.email, self.passwd), headers=self.headers)
        else:
            response = requests.get(self.jira_adress+"/rest/api/2/search?jql=cf[11200]="+
                self.epic_key+"|key="+self.epic_key+"&fields=issuetype,status,created,project,parent,customfield_11200"+
                "&expand=changelog&maxResults=200",auth=(self.email, self.passwd), headers=self.headers)

        if(response.status_code != 200):
            print(response.status_code) 
            return #TODO lancer une exception
        json = response.json()
        max_results = json["maxResults"]
        nb_of_pages = math.ceil(json["total"]/max_results)
        print("max results: " + str(max_results) + " json total: " + str(json["total"]))
        changelogs= response.json()["issues"]

        for i in range(0, nb_of_pages):
            if(i>0):
                print(str(i)+"/"+str(nb_of_pages))
                if(self.epic_key == ""):
                    response = requests.get(self.jira_adress+"/rest/api/2/search?jql=project="+
                        self.project_key+"&fields=issuetype,status,created,project,parent"+
                        "&expand=changelog&maxResults=200&startAt="+str(i*max_results),auth=(self.email, self.passwd), headers=self.headers)
                else:
                    response = requests.get(self.jira_adress+"/rest/api/2/search?jql=cf[11200]="+
                        self.epic_key+"|key="+self.epic_key+"&fields=issuetype,status,created,project,parent,customfield_11200"+
                        "&expand=changelog&maxResults=200&startAt="+str(i*max_results),auth=(self.email, self.passwd), headers=self.headers)
                changelogs.extend(response.json()["issues"])

        return changelogs

    def transform_changelogs(self,changelogs):
        log_list = []
        for issue in changelogs:
            new_status_tuple = self.new_status_dict[issue["fields"]["issuetype"]["id"]]
            log = self.create_log(issue, issue["fields"]["created"], new_status_tuple[0], new_status_tuple[1])
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
        log["timestamp"] = timestamp
        log["id"] = int(issue["id"])
        log["key"] = issue["key"]
        log["project_id"] = int(issue["fields"]["project"]["id"])
        log["project_key"] = issue["fields"]["project"]["key"]
        if(issue["fields"].get("parent") is not None):
            log["parent_id"] = int(issue["fields"]["parent"]["id"])
            log["parent_key"] = issue["fields"]["parent"]["key"]
        elif(issue["fields"].get("customfield_11200") is not None):
            log["parent_key"] = issue["fields"]["customfield_11200"]
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

        for project in project_list:
            if(project["key"] == self.project_key):
                return project["id"]
        return None

    def get_new_statuses(self):
        """
        return a dict containing the id and name of the new status for each issue type
        """
        status_list_response = requests.get(self.jira_adress+"/rest/api/2/project/"+self.project_id+"/statuses",
            auth=(self.email, self.passwd), headers=self.headers)
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

    def save_logs_in_csv(self,file_path):
        """
        Save a list of Jira logs as a csv file
        """
        if(not file_path.endswith(".csv")):
            file_path = file_path+".csv"
        fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
        with open(file_path, 'w', encoding="UTF-8", newline='') as file:
            write = csv.writer(file)
            write.writerow(fields)
            for log in self.log_list:
                write.writerow(log.values())

    def save_logs_in_json(self,file_path):
        """
        Save a list of Jira logs as a json file
        """
        if(not file_path.endswith(".json")):
            file_path = file_path+".json"
        with open(file_path,'w',encoding="UTF=8") as file:
            json.dump(self.log_list,file)


def main(argv):
    """
    This script gather logs on a Jira server and save then in a csv file, for now
    """
    project_name = None
    output_file = None
    output_type = None
    jira_type = "cloud"
    epic_key=""
    try:
        opts, args = getopt.getopt(argv,"e:p:t:o:s",["epickey=","project=","otype=","ofile=","server"])
    except getopt.GetoptError:
        print("jirascript.py -p <projectkey> -t <outputtype> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--projectkey"):
            project_name = arg
        elif opt in ("-t", "--outputtype"):
            if arg in ("csv","json"):
                output_type = arg
            else:
                sys.exit(2)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-s","--server"):
            jira_type = "server"
        elif opt in ("-e", "--epickey"):
            epic_key = arg
    config = configparser.ConfigParser()
    config.read('../config.cfg')
    jira_exp = JiraExporter(config, jira_type, project_name, epic_key)
    results = jira_exp.run()
    if(output_type == "csv"):
        jira_exp.save_logs_in_csv(output_file)
    else:
        jira_exp.save_logs_in_json(output_file)

if __name__ == "__main__":
    main(sys.argv[1:])

#TODO
"""
Un potentiel problème est si l'historique de changement comporte plus de 100 entrées. Si cela devient une
limitation il faudra alors faire un appel sur GET /rest/api/3/issue/{issueIdOrKey}/changelog

Pour rendre les champs que l'on récupère totalement paramétrables, créer une fonction récursive qui explore
les champs et les dictionnaires retournés: exemple si le chemin d'un champs est /fields/trucA/trucB alors il faudra
un premier appel pour récupérer le dict fields, un autre pour récupérer le dict trucA et enfin un appel terminal pour accéder
champ trucB.

Pour réduire le temps d'exécution on pourrait modifier les requêtes pour ne retourner que les champs nécessaires, cela réduirait
le payload des réponses
"""