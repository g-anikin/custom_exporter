import requests
import os
import json
requests.packages.urllib3.disable_warnings()

def get_auth_token(username, password, sast_host):
    api = '/cxrestapi/auth/identity/connect/token'
    final_url = sast_host + api
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    post_fields = {
        "username": username,
        "password": password,
        "grant_type": 'password',
        "scope": 'sast_rest_api',
        "client_id": 'resource_owner_client',
        "client_secret": '014DF517-39D1-4453-B7B3-9930C563627C',
    }
    response = requests.post(final_url,
                             data=post_fields,
                             headers=headers,
                             verify=False,
                             timeout=3)
    json_obj = json.loads(response.text)
    #print(json_obj)
    return json_obj['access_token']


def get_current_queue(token, sast_host):
    api = '/cxrestapi/sast/scansQueue'
    final_url = sast_host + api
    headers = {"Content-Type": "application/json;v=1.0",
               "Accept": "application/json",
               "Authorization": "Bearer " + token}
    response = requests.get(final_url, headers=headers, verify=False, timeout=3)
    response_as_json = response.json()
    #print(response_as_json)
    queue_count = len(response_as_json)
    return queue_count


def sast_queue_len(gauge_sast_queue_len):
    username = os.environ.get('KSPD_SAST_QUEUE_USER')
    password = os.environ.get('KSPD_SAST_QUEUE_PASSWORD')
    sast_host = os.environ.get('KSPD_SAST_HOST')
    #print(username,password,sast_host)
    token = get_auth_token(username, password, sast_host)
    queue_count = get_current_queue(token, sast_host)
    gauge_sast_queue_len.add_metric([sast_host], queue_count)
