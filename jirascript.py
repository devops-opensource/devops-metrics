import sys,getopt
import requests
import math
import csv
import configparser
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class JiraCloud:
    def __init__(self, config, jira_token, project_key):
        self.email = config["JIRA_CLOUD"]["jira_user_email"]
        self.token = jira_token
        self.jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
        self.project_key = project_key

        self.df_versions = pd.DataFrame()

    def create_session(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        } 
        session = requests.Session()
        session.auth = (self.email, self.token)
        session.headers.update(headers)
        return session

    def execute_project_version_request(self, parameters, is_recursive = True):
        version_url = f"{self.jira_adress}/rest/api/2/project/{self.project_key}/version?"
        parameters_string = f"{parameters}" if parameters else ""

        version_query = f"{version_url}{parameters_string}"

        with self.create_session() as session:
            response = session.get(version_query)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)

        response_json = response.json()
        issues = response_json["values"]
        total = response_json["total"]
        current_issue = 200

        if not is_recursive:
            return issues
        
        with ThreadPoolExecutor(max_workers = 20) as executor:
            threads = []
            print(f"Total issues: {total}")
            while(current_issue < total):
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAT={current_issue}"
                threads.append(executor.submit(self.execute_project_version_request, next_parameters, is_recursive = False))
                current_issue += 200
        for task in as_completed(threads):
            issues.extend(task.results())
        
        return issues

    def execute_jql_request(self, query, fields, parameters, is_recursive=True):
        jira_url = f"{self.jira_adress}/rest/api/2/search?"

        fields_string = f"&fields={fields}" if fields else None
        parameter_string = f"&{parameters}" if parameters else None
        query_string = f"jql={query}"

        with self.create_session() as session:
            response = session.get(f"{jira_url}{query_string}{fields_string}{parameter_string}")
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        
        response_json = response.json()
        issues = response_json["issues"]
        total = response_json["total"]
        current_issue = 200
        if not is_recursive:
            return issues

        with ThreadPoolExecutor(max_workers = 20) as executor:
            threads = []
            print(f"Total issues: {total}")
            while(current_issue < total):
                print(f"startAt={current_issue}")
                next_parameters = f"{parameters}&startAT={current_issue}"
                threads.append(executor.submit(self.execute_jql_request, query, fields, next_parameters, is_recursive = False))
                current_issue += 200
        for task in as_completed(threads):
            issues.extend(task.results())
        
        return issues

    def extract_versions(self):
        parameters = "maxResults=200"
        versions = self.execute_project_version_request(parameters)
        return versions
    
    def transform_versions(self, versions):
        
        fieldnames_mapping = {
            "name" : "name",
            "description" : "description",
            "releaseDate" : "release_date",
            "startDate" : "start_date"
        }
        fields_to_keeps = ["name", "description", "release_date", "start_date"]
        df_versions = pd.json_normalize(versions)
        df_versions = df_versions.rename(columns = fieldnames_mapping)
        # df_versions = df_versions[df_versions["released"]==True]
        if("release_date" in df_versions):
            df_versions["release_date"] = pd.to_datetime(df_versions["release_date"], utc=True, errors="coerce")
        else:
            df_versions["release_date"] = None
        if("start_date" in df_versions):
            df_versions["start_date"] = pd.to_datetime(df_versions["start_date"], utc=True, errors="coerce")
        else:
            df_versions["start_date"] = None
        df_versions = self.df_drop_columns(df_versions,fields_to_keeps)

        df_versions["event_type"] = "release_management"
        df_versions["project_key"] = self.project_key
        df_versions["control_date"] = df_versions["release_date"]

        return df_versions

    def get_release_management(self):
        if(self.df_versions.empty):
            versions = self.extract_versions()
            transformed_versions = self.transform_versions(versions)
            self.df_versions = transformed_versions
        return self.df_versions

    def extract_status_changelogs(self):
        fields = f"issuetype,status,created,project,parent,fixVerions"
        parameters = f"expand=changelogs&maxResults=200"
        query = f"project={self.project_key} AND issuetype in (Story)"

        changelogs = self.execute_jql_request(query, fields, parameters)

        return changelogs
    
    def transform_status_changelogs(self, changelogs):
        fieldnames_mapping = {
            "key" : "key",
            "fields.project.key" : "project_key",
            "fields.parent.key" : "parent_key",
            "fields.issuetype.name" : "issue_type",
            "fromString" : "from_status",
            "toSring" : "to_status",
            "changelog.histories.created" : "to_date",
            "name" : "version"
            }
        fields_to_keep = ["key", "project_key", "parent_key", "issue_type", "from_status", "to_status",
        "to_date", "version"]
        
        return 

    def df_drop_columns(self, dataframe, columns_to_keep):
        for col in dataframe.columns:
            if col not in columns_to_keep:
                dataframe = dataframe.drop(columns=col)
        return dataframe

def get_status_change_logs(jira_type,project_name,epic_key,config):
    """
    Get ticket logs from a jira server
    """
    if(jira_type == "server"):
        email = config["JIRA_SERVER"]["jira_user_email"]
        passwd = config["JIRA_SERVER"]["jira_user_password"]
        jira_adress = config["JIRA_SERVER"]["jira_server_url"]
    else:
        email = config["JIRA_CLOUD"]["jira_user_email"]
        passwd = config["JIRA_CLOUD"]["jira_user_token"]
        jira_adress = config["JIRA_CLOUD"]["jira_cloud_url"]
    
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    }
    project_list_response = requests.get(jira_adress+"/rest/api/2/project",auth=(email, passwd), headers=headers)
    if(project_list_response.status_code != 200):
        print(project_list_response.content)
        return #TODO lancer une exception

    project_id = get_project_id(project_name,project_list_response.json())

    status_list_response = requests.get(jira_adress+"/rest/api/2/project/"+project_id+"/statuses",auth=(email, passwd), headers=headers)
    if(status_list_response.status_code != 200):
        print(status_list_response.content)
        return #TODO lancer une exception

    new_statuses = get_new_statuses(status_list_response.json())
    
    if(epic_key == ""):
        response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
            project_name+"&fields=issuetype,status,created,project,parent"+
            "&expand=changelog&maxResults=200",auth=(email, passwd), headers=headers)
    else:
        response = requests.get(jira_adress+"/rest/api/2/search?jql=cf[11200]="+
            epic_key+"|key="+epic_key+"&fields=issuetype,status,created,project,parent,customfield_11200"+
            "&expand=changelog&maxResults=200",auth=(email, passwd), headers=headers)

    if(response.status_code != 200):
        print(response.status_code) 
        return #TODO lancer une exception
        
    json = response.json()
    max_results = json["maxResults"]
    nb_of_pages = math.ceil(json["total"]/max_results)
    
    log_list=[]

    for i in range(0, nb_of_pages):
        if(i>0):
            print(str(i)+"/"+str(nb_of_pages))
            if(epic_key == ""):
                response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
                    project_name+"&fields=issuetype,status,created,project,parent"+
                    "&expand=changelog&maxResults=200&startAt="+str(i*max_results),auth=(email, passwd), headers=headers)
            else:
                response = requests.get(jira_adress+"/rest/api/2/search?jql=cf[11200]="+
                    epic_key+"|key="+epic_key+"&fields=issuetype,status,created,project,parent,customfield_11200"+
                    "&expand=changelog&maxResults=200&startAt="+str(i*max_results),auth=(email, passwd), headers=headers)
            json = response.json()
        issue_list = json["issues"]
        for issue in issue_list:
            new_status_tuple = new_statuses[issue["fields"]["issuetype"]["id"]]
            log = create_log(issue, issue["fields"]["created"], new_status_tuple[0], new_status_tuple[1])
            log_list.append(log)
            for changelog in issue["changelog"]["histories"]:
                for item in changelog["items"]:
                    if(item["field"]=="status"):
                        log = create_log(issue,changelog["created"],item["to"],item["toString"])
                        log_list.append(log)

    return log_list

def create_log(issue, timestamp, status_id, status_name):
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

def get_project_id(project_key, project_list):
    """
    return the id associated to a project key in a project list
    """
    for project in project_list:
        if(project["key"] == project_key):
            return project["id"]
    return None

def get_new_statuses(status_list):
    """
    return a dict containing the id and name of the new status for each issue type
    """
    new_status_dict = dict() 
    for ticket in status_list:
        for status in ticket["statuses"]:
            if(status["statusCategory"]["key"]=="new"):
                new_status_dict[ticket["id"]]=(status["id"],status["name"])
    return new_status_dict

def save_logs_in_csv(file_path, log_list):
    """
    Save a list of Jira logs as a csv file
    """
    if(not file_path.endswith(".csv")):
        file_path = file_path+".csv"
    fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
    with open(file_path, 'w', encoding="UTF-8", newline='') as file:
        write = csv.writer(file)
        write.writerow(fields)
        for log in log_list:
            write.writerow(log.values())

def save_logs_in_json(file_path, log_list):
    """
    Save a list of Jira logs as a json file
    """
    if(not file_path.endswith(".json")):
        file_path = file_path+".json"
    with open(file_path,'w',encoding="UTF=8") as file:
        json.dump(log_list,file)

