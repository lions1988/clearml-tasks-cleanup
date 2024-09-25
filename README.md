# ClearML Tasks Cleanup


## Pull tasks for review before deletion 

Generate tasks list from ClearML, limited for spesific `username` and task `last_changed` timestamp

##### Required arguments
* `--username` : ClearML full username, e.g `Lion S`
* `--delete_threshold_days` : limit query to tasks older then `delete_threshold_days` days

### Usage 

##### Pull `Lion S` tasks older then `180` days
```
python pull_clearml_tasks.py --username Lion S --delete_threshold_days 180
```

##### Tasks json output exmaple
```
{
        "task_id": "18342f1019c04630za1a14029bec791",
        "task_name": "docfm_v7_safe_32gpu80g_11Jan24_6w",
        "task_url": "https://<clearml_url>:8080/projects/1c02916ceba84b15a1ecb6686d93a4d1/experiments/18342f1019c04630848ec14029bec791",
        "user": "a33e22b207a1d113ca5cbfddd5d94b9d8f2",
        "status": "stopped",
        "created": "2024-01-11T13:48:56.559000+00:00",
        "last_changed": "2024-01-11T19:07:58.823000+00:00",
        "project_id": "1c02916cebaq1vg5a1ecb6686d93a4d1",
        "project_name": "FoundationModelsDocuments"
},
```


### Pre-req 

* Run from existing ClearML enviornemt (`~/clearml.conf` is already configured)
* Setup ClearML URL and secrets for API access
```
export clearml_url=https://<clearml_url>
export clearml_access_key=<clearml_access_key>
export clearml_secret_key=<clearml_secret_key>
```
* Set `delete_threshold_days` - pull all tasks older then `delete_threshold_days`

## Delete tasks 

Run the `delete_clearml_tasks` and point to tasks json file 

 ##### Required arguments
* `--tasks_json` : full path to tasks json list 

```
python delete_clearml_tasks.py --tasks_json <full_path_to_tasks_json>
```

