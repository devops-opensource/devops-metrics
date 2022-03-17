import sys,getopt
import requests
import math
import csv
import configparser

def get_status_change_logs(project_name, config):
    """
    Get ticket logs from a jira server
    """
    email = config["JIRA"]["jira_user_email"]
    access_token = config["JIRA"]["jira_user_token"]
    jira_adress = config["JIRA"]["jira_server_url"]
    headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    }
    project_list_response = requests.get(jira_adress+"/rest/api/2/project",auth=(email, access_token), headers=headers)
    if(project_list_response.status_code != 200):
        return #TODO ajouter un message d'erreur

    project_id = get_project_id(project_name,project_list_response.json())

    status_list_response = requests.get(jira_adress+"/rest/api/2/status",auth=(email, access_token), headers=headers)
    if(status_list_response.status_code != 200):
        return #TODO ajouter un message d'erreur

    new_status = get_new_status(project_id,status_list_response.json())
    
    response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
        project_name+"&expand=changelog",auth=(email, access_token), headers=headers)

    if(response.status_code != 200):
        return #TODO ajouter un message d'erreur
        
    json = response.json()
    max_results = json["maxResults"]
    nb_of_pages = math.ceil(json["total"]/max_results)
    
    log_list=[]

    for i in range(0, nb_of_pages):
        if(i>0):
            response = requests.get(jira_adress+"/rest/api/2/search?jql=project="+
                project_name+"&expand=changelog&startAt="+str(i*max_results),auth=(email, access_token), headers=headers)
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
    fields = ["timestamp","id","key","project_id","project_key","parent_id","parent_key","type_id","type_name","status_id","status_name"]
    with open(file_path, 'w', encoding="UTF-8") as file:
        write = csv.writer(file)
        write.writerow(fields)
        for log in log_list:
            write.writerow(log.values())

def main(argv):
    """
    This script gather logs on a Jira server and save then in a csv file, for now
    """
    project_name = None
    output_file = None
    try:
        opts, args = getopt.getopt(argv,"p:o:",["project=","ofile="])
    except getopt.GetoptError:
        print("jirascript.py -p <projectkey> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--projectkey"):
            project_name = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
    config = configparser.ConfigParser()
    config.read('config.cfg')
    results = get_status_change_logs(project_name,config)
    save_logs_in_csv(output_file,results)

if __name__ == "__main__":
    main(sys.argv[1:])
