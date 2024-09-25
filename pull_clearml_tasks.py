from clearml.backend_api.session.client import APIClient
import datetime
from datetime import datetime
import time
from time import time
import argparse
import json
import os
import requests
import tqdm
import urllib3
import sys


def verify_clearml_keys(clearml_access_key,clearml_secret_key):
    if clearml_access_key is None:
        raise Exception("clearml_access_key is missing")
    
    if clearml_secret_key is None:
        raise Exception("clearml_secret_key is missing")

    if clearml_url is None:
        raise Exception("clearml_url is missing")

def pull_users():
        
        all_users = []
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(clearml_users_api_endpoint,auth=clearml_auth,verify=False)

        data = response.json()
        all_users = data['data']['users']

        users_dict = {user["id"]: user["name"] for user in all_users}

        return users_dict

def match_user_id(users_dict, username):
    for user_id, name in users_dict.items():
        if name == username:
            return user_id

def pull_tasks(user,delete_threshold_days):

        client = APIClient()
        timestamp = time() - 60 * 60 * 24 * delete_threshold_days
        page = 0
        page_size = 500
        total_tasks_pulled = 0
        
        task_list = []
    
        print(f"\033[1;92mINFO: Pulling {username} tasks older then {delete_threshold_days} days\033[0m")

        while True:
            tasks = client.tasks.get_all(
                user=[user],
                only_fields=["id", "name", "created", "status_changed", "status","user","project"],
                order_by=["-last_update"],
                page_size=page_size,
                page=page,
                status_changed=["<{}".format(datetime.fromtimestamp(timestamp))]
            )
    
            num_tasks = len(tasks)
            total_tasks_pulled += num_tasks
    
            print(f"INFO: Page {page}, Number of tasks pulled: {num_tasks}")
    
            if not tasks:
                print("INFO: Done - no tasks returned")
                break
            
            for task in tqdm.tqdm(tasks):
                try:
                    task_url = f"{clearml_url}:8080/projects/{task.project}/experiments/{task.id}"

                    task_data = {
                        "task_id": task.id,
                        "task_name": task.name,
                        "task_url": task_url,
                        "user": task.user,
                        "status": task.status.value,
                        "created": task.created.isoformat(),
                        "last_changed": task.status_changed.isoformat(),
                        "project_id": task.project
                    }
                    task_list.append(task_data)
    
                except AttributeError as e:
                    print(f"Error")
     
            page += 1
    
        with open(tasks_json, 'w') as json_file:
            json.dump(task_list, json_file, indent=4)
        os.chmod(tasks_json, 0o755)

        print(f"INFO: Total number of tasks pulled: {total_tasks_pulled}")
        
def pull_projects():

        page = 0
        page_size = 500
        all_projects = []

        print("INFO: Pulling projects names")
        while True:
            json_body = {
                'page': page,
                'page_size': page_size,
                'only_fields': ['id','name']
            }
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(clearml_projects_api_endpoint,json=json_body,auth=clearml_auth,verify=False)

            data = response.json()
            projects = data['data']['projects']

            if len(projects) == 0:
                print("INFO: Done - no projects returned")                
                break    
            
            all_projects.extend(projects)
            page += 1


        return all_projects

def match_project_name():

    with open(tasks_json, 'r') as f:
        tasks = json.load(f)

    print("INFO: Matching project names")            
    project_dict = {project["id"]: project["name"] for project in all_projects}    
    for task in tqdm.tqdm(tasks):
        project_id = task["project_id"]
        if project_id in project_dict:
             task["project_name"] = project_dict[project_id]
    with open(tasks_json, 'w') as f:
        json.dump(tasks, f, indent=4)             
    return tasks              


### main ###

parser = argparse.ArgumentParser(description='Limit ClearML tasks to user/delete_threshold_days')
parser.add_argument('--username', nargs='+', type=str, help='limit query to specific user ID, e.g --username <clearml_display_name>', required=True)
parser.add_argument('--delete_threshold_days', type=float, help='get tasks older then xxx days, e.g --delete_threshold_days 180, show tasks older then 180 days', required=True)
args = parser.parse_args()

clearml_url = os.getenv('clearml_url')
clearml_access_key = os.getenv('clearml_access_key')
clearml_secret_key = os.getenv('clearml_secret_key')
clearml_auth = (clearml_access_key, clearml_secret_key)
clearml_projects_api_endpoint = f"{clearml_url}:8008/projects.get_all"
clearml_users_api_endpoint = f"{clearml_url}:8008/users.get_all"


users_dict = pull_users()

username = ' '.join(args.username)
user_id = match_user_id(users_dict, username)
if user_id:
    user = user_id
else:
    print(f"INFO: ERROR --- Username '{username}' not found")
    sys.exit(1)

tasks_json = f"tasks_user_{user}_{args.delete_threshold_days}_days.json"

verify_clearml_keys(clearml_access_key,clearml_secret_key)

pull_tasks(user,args.delete_threshold_days)

all_projects = pull_projects()

match_project_name()

print(f"\033[1;92mINFO: Dumped tasks data to {os.path.abspath(tasks_json)}\033[0m")
