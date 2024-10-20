import argparse
import json
import os
import requests
import tqdm
import urllib3
import re


def match_user_secrets(clearml_conf_file):
    
    clearml_conf_file = os.path.expanduser(clearml_conf_file)
    clearml_api_endpoint = None
    clearml_access_key = None
    clearml_secret_key = None
    
    url_pattern = re.compile(r'api_server\s*:\s*(https?://\S+)')
    access_key_pattern = re.compile(r'"access_key"\s*=\s*"(.+?)"')
    secret_key_pattern = re.compile(r'"secret_key"\s*=\s*"(.+?)"')
    
    with open(clearml_conf_file, 'r') as f:
        data = f.read()
        
        url_match = url_pattern.search(data)
        clearml_api_endpoint = url_match.group(1)
        
        access_key_match = access_key_pattern.search(data)
        clearml_access_key = access_key_match.group(1)
        
        secret_key_match = secret_key_pattern.search(data)
        clearml_secret_key = secret_key_match.group(1)
        
    return clearml_api_endpoint, clearml_access_key, clearml_secret_key


def delete_tasks():

        with open(tasks_json, 'r') as json_file:
            tasks = json.load(json_file)
        
        print(f"INFO: Starting deleting tasks from {tasks_json}")

        for task in tqdm.tqdm(tasks):
            task_id = task.get('task_id')
            task_name = task.get('task_name')
            project_name = task.get('project_name')
            json_body = {
                 "task": task_id,
                 "force" : True,
                 "delete_output_models" : True,
            }
            
            full_task_name = f"{project_name}/{task_name}"
            print(f"INFO: Deleting task --- {full_task_name} ")
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(clearml_tasks_delete_api_endpoint, auth=clearml_auth, headers={"Content-Type": "application/json"}, json=json_body, verify=False)

            if response.status_code == 200:
                print(f"INFO: OK --- TASK DELETED")
            elif response.status_code == 400:
                print(f"INFO: ERROR --- TASK NOT FOUND")
            else:
                print(f"Unexpected response: {response.status_code}")


### main ###

parser = argparse.ArgumentParser(description='Delete ClearML tasks from stastic json')
parser.add_argument('--tasks_json', type=str, help='Point to static tasks_json list of ClearML tasks', required=True)
args = parser.parse_args()


clearml_conf_file = '~/clearml.conf'
clearml_api_endpoint, clearml_access_key, clearml_secret_key = match_user_secrets(clearml_conf_file)
clearml_auth = (clearml_access_key, clearml_secret_key)
clearml_projects_api_endpoint = f"{clearml_api_endpoint}/projects.get_all"
clearml_tasks_delete_api_endpoint = f"{clearml_api_endpoint}/tasks.delete"


tasks_json = args.tasks_json
