import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning 
import os

def get_status_jenkins(gauge_dso_service):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url_list = [os.environ.get('KSPD_JENKINS_HOST')]
    user_list = [os.environ.get('KSPD_JENKINS_USER')]
    token_list = [os.environ.get('KSPD_JENKINS_TOKEN')]
    for i in range(0, len(url_list)):
        while True:
            try:
                resp = requests.get(url_list[i], auth=(user_list[i], token_list[i]), timeout=10, verify=False)
                if resp.status_code == 200:
                    gauge_dso_service.add_metric(['jenkins', url_list[i]], 1)
                else:
                    gauge_dso_service.add_metric(['jenkins', url_list[i]], 0)
            except requests.exceptions.ConnectTimeout:
                gauge_dso_service.add_metric(['jenkins', url_list[i]], 0)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            break


def get_status_ghe(gauge_dso_service):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url_list = [os.environ.get('KSPD_GHE_HOST')]
    for i in range(0, len(url_list)):
        while True:
            try:
                resp = requests.get(url_list[i], timeout=10, verify=False)
                if resp.status_code == 200 and "GitHub lives!" in resp.text:
                    gauge_dso_service.add_metric(['ghe', url_list[i]], 1)
                else:
                    gauge_dso_service.add_metric(['ghe', url_list[i]], 0)
            except requests.exceptions.ConnectTimeout:
                gauge_dso_service.add_metric(['ghe', url_list[i]], 0)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            break

def get_status_sast(gauge_dso_service):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url_list = [os.environ.get('KSPD_SAST_HOST')]
    user_list = [os.environ.get('KSPD_SAST_USER')]
    password_list = [os.environ.get('KSPD_SAST_PASSWORD')]
    client_id_list = [os.environ.get('KSPD_SAST_CLIENT_ID')]
    secret_list = [os.environ.get('KSPD_SAST_SECRET')]
    for i in range(0, len(url_list)):
        post_fields = {
            "username": user_list[i],
            "password": password_list[i],
            "grant_type": 'password',
            "scope": 'sast_rest_api',
            "client_id": client_id_list[i],
            "client_secret": secret_list[i],
        }
        while True:
            try:
                resp = requests.post(url_list[i], data=post_fields, timeout=10, verify=False)
                if resp.status_code == 200:
                    gauge_dso_service.add_metric(['sast', url_list[i]], 1)
                else:
                    gauge_dso_service.add_metric(['sast', url_list[i]], 0)
            except requests.exceptions.ConnectTimeout:
                gauge_dso_service.add_metric(['sast', url_list[i]], 0)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            break

def get_status_nexus(gauge_dso_service, gauge_nexus_service):
    url_list = [os.environ.get('KSPD_NEXUS_HOST')]
    user_list = [os.environ.get('KSPD_NEXUS_USER')]
    password_list = [os.environ.get('KSPD_NEXUS_PASSWORD')]
    for i in range(0, len(url_list)):
        while True:
            try:
                resp = requests.get(url_list[i], auth=(user_list[i], password_list[i]), timeout=10, verify=False)
                if resp.status_code == 200:
                    gauge_dso_service.add_metric(['nexus', url_list[i]], 1)
                    json_response = resp.json()
                    for i in json_response:
                        gauge_nexus_service.add_metric([i.lower().replace(' ','_')], int(json_response[i]['healthy']))
                else:
                    gauge_dso_service.add_metric(['nexus', url_list[i]], 0)
            except requests.exceptions.ConnectTimeout:
                gauge_dso_service.add_metric(['nexus', url_list[i]], 0)
            except requests.exceptions.ConnectionError:
                continue
            except requests.exceptions.ReadTimeout:
                continue
            break

def get_status_artifactory(gauge_dso_service, gauge_artifactory_service, gauge_artifactory_node, gauge_artifactory_check_page):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url_list = [os.environ.get('KSPD_ARTIFACTORY_HOST')]
    token_list = [os.environ.get('KSPD_ARTIFACTORY_TOKEN')]
    url_final = ['artifactory/api/system/ping', 'ui/api/v1/system/status/nodes', 'artifactory/api/system/status',]
    for i in range(0, len(url_list)):
        headers = {
            'X-JFrog-Art-Api': token_list[i]
        }
        for j in url_final:
            if j == 'artifactory/api/system/ping':
                try:
                    resp = requests.get(url_list[i]+j, headers=headers, timeout=10, verify=False)
                    if resp.status_code == 200:
                        gauge_dso_service.add_metric(['artifactory', url_list[i]+j], 1)
                    else:
                        gauge_dso_service.add_metric(['artifactory', url_list[i]+j], 0)
                except requests.exceptions.ConnectTimeout:
                    gauge_dso_service.add_metric(['artifactory', url_list[i]+j], 0)
            elif j == 'ui/api/v1/system/status/nodes':
                try:
                    resp = requests.get(url_list[i]+j, headers=headers, timeout=10, verify=False)
                    if resp.status_code == 200:
                        gauge_artifactory_check_page.add_metric([url_list[i]+j], 1)
                        json_response = resp.json()
                        for k in json_response:
                            try:
                                if k['state'] == 'HEALTHY':
                                    gauge_artifactory_service.add_metric([k['name']], 1)
                                else:
                                    gauge_artifactory_service.add_metric([k['name']], 0)
                            except KeyError:
                                continue
                    else:
                        gauge_artifactory_check_page.add_metric([url_list[i]+j], 0)
                except requests.exceptions.ConnectTimeout:
                    gauge_artifactory_check_page.add_metric([url_list[i]+j], 0)
            elif j == 'artifactory/api/system/status':
                try:
                    resp = requests.get(url_list[i]+j, headers=headers, timeout=10, verify=False)
                    if resp.status_code == 200:
                        gauge_artifactory_check_page.add_metric([url_list[i]+j], 1)
                        json_response = resp.json()
                        artifactory_nodes = json_response['nodes']
                        for k in artifactory_nodes:
                            if k['state'] == 'RUNNING':
                                gauge_artifactory_node.add_metric([k['id']], 1)
                            else:
                                gauge_artifactory_node.add_metric([k['id']], 0)
                    else:
                        gauge_artifactory_check_page.add_metric([url_list[i]+j], 0)
                except requests.exceptions.ConnectTimeout:
                    gauge_artifactory_check_page.add_metric([url_list[i]+j], 0)