import sys,getopt
import requests
import math
import csv
import configparser
import json

def get_status_change_logs(jira_type,project_name, config):
    """
    Get ticket logs from a jira server
    """
    if(jira_type == "server"):
        email = config["JIRA_SERVER"]["jira_user_email"]
        passwd = config["JIRA_SERVER"]["jira_user_token"]
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
        return #TODO ajouter un message d'erreur

    project_id = get_project_id(project_name,project_list_response.json())

    status_list_response = requests.get(jira_adress+"/rest/api/2/status",auth=(email, passwd), headers=headers)
    if(status_list_response.status_code != 200):
        return #TODO ajouter un message d'erreur

    new_status = get_new_status(project_id,status_list_response.json())
    
    response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
        project_name+"&expand=changelog",auth=(email, passwd), headers=headers)

    if(response.status_code != 200):
        return #TODO ajouter un message d'erreur
        
    json = response.json()
    max_results = json["maxResults"]
    nb_of_pages = math.ceil(json["total"]/max_results)
    
    log_list=[]

    for i in range(0, nb_of_pages):
        if(i>0):
            response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
                project_name+"&expand=changelog&startAt="+str(i*max_results),auth=(email, passwd), headers=headers)
            json = response.json()
        issue_list = json["issues"]
        for issue in issue_list:
            log = create_log(issue, issue["fields"]["created"], new_status[0], new_status[1])
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
    log["id"] = issue["id"]
    log["key"] = issue["key"]
    log["project_id"] = issue["fields"]["project"]["id"]
    log["project_key"] = issue["fields"]["project"]["key"]
    if(issue["fields"].get("parent") is not None):
        log["parent_id"] = issue["fields"]["parent"]["id"]
        log["parent_key"] = issue["fields"]["parent"]["key"]
    else:
        log["parent_id"] = "null"
        log["parent_key"] = "null"
    log["type_id"] = issue["fields"]["issuetype"]["id"]
    log["type_name"] = issue["fields"]["issuetype"]["name"]
    log["status_id"] = status_id
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

def get_new_status(project_id, status_list):
    """
    return the id of the status assigned to new tickets
    """
    for status in status_list:
        if(status.get("scope") is not None
        and status["scope"]["type"]=="PROJECT"
        and status["scope"]["project"]["id"] == str(project_id)
        and status["statusCategory"]["key"] == "new"):
            return (status["id"],status["untranslatedName"])
    return None

def save_logs_in_csv(file_path, log_list):
    """
    Save a list of Jira logs as a csv file
    """
    if(not file_path.endswith(".csv")):
        file_path = file_path+".csv"
    fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
    with open(file_path, 'w', encoding="UTF-8") as file:
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

def elk_create_new_index(index_name,config):
    """
    Create a new index in the elasticsearch instance
    """
    elk_url = config["ELK"]["ELASTICSEARCH_URL"]
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    }
    with open("mapping.json",'r',encoding="UTF=8") as file:
        mapping = json.load(file)
        response = requests.put(elk_url+"/"+index_name,headers=headers,data=mapping)


def main(argv):
    """
    This script gather logs on a Jira server and save then in a csv file, for now
    """
    project_name = None
    output_file = None
    output_type = None
    jira_type = "cloud"
    try:
        opts, args = getopt.getopt(argv,"p:t:o:",["project=","otype=","ofile="])
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
    config = configparser.ConfigParser()
    config.read('config.cfg')
    results = get_status_change_logs(jira_type,project_name,config)
    if(output_type == "csv"):
        save_logs_in_csv(output_file,results)
    else:
        save_logs_in_json(output_file,results)

if __name__ == "__main__":
    main(sys.argv[1:])
