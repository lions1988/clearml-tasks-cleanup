import argparse
import json
import os
import requests
import tqdm
import urllib3



def verify_clearml_keys(clearml_access_key,clearml_secret_key):
    if clearml_access_key is None:
        raise Exception("clearml_access_key is missing")
    
    if clearml_secret_key is None:
        raise Exception("clearml_secret_key is missing")

    if clearml_url is None:
        raise Exception("clearml_url is missing")


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

clearml_url = os.getenv('clearml_url')
clearml_access_key = os.getenv('clearml_access_key')
clearml_secret_key = os.getenv('clearml_secret_key')
clearml_auth = (clearml_access_key, clearml_secret_key)
clearml_tasks_delete_api_endpoint = f"{clearml_url}:8008/tasks.delete"

tasks_json = args.tasks_json

verify_clearml_keys(clearml_access_key,clearml_secret_key)

delete_tasks()
