import json
import requests
import os
requests.packages.urllib3.disable_warnings()
from dotenv import load_dotenv
load_dotenv()



# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
    }

basicauth = ("admin", "cisco")
studentID = os.environ.get("STUDENT_ID")
last3 = studentID[-3:]
x = int(last3[0])
y = int(last3[1:])


def create(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code == 200:
        print(f"Interface Loopback{studentID} already exists on {ip_address}")
        return f"Cannot create: Interface loopback {studentID}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{studentID}",
            "description": f"Loopback interface for {studentID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": f"172.{x}.{y}.1",
                        "netmask": "255.255.255.0"
                    }
                ]
            },
            "ietf-ip:ipv6": {}
        }
    }

    resp = requests.put(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if 200 <= resp.status_code <= 299:
        print(f"STATUS OK: {resp.status_code}")
        return f"Interface loopback {studentID} is created successfully using Restconf"
    elif resp.status_code == 409:
        print("Interface already exists (Conflict 409)")
        return f"Cannot create: Interface loopback {studentID}"
    else:
        print(f"Error. Status Code: {resp.status_code}")
        return f"Cannot create: Interface loopback {studentID}"

def delete(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)

    if check.status_code != 200:
        print(f"[RESTCONF] Interface Loopback{studentID} not found on {ip_address}")
        return f"Cannot delete: Interface loopback {studentID}"

    resp = requests.delete(
        api_url, 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )
    if 200 <= resp.status_code <= 299:
        print(f"[RESTCONF] Deleted successfully: {resp.status_code}")
        return f"Interface loopback {studentID} is deleted successfully using Restconf"
    elif resp.status_code == 404:
        print(f"[RESTCONF] Loopback{studentID} not found (404)")
        return f"Cannot delete: Interface loopback {studentID}"
    else:
        print(f"[RESTCONF] Error deleting interface. Code: {resp.status_code}")
        return f"Cannot delete: Interface loopback {studentID}"


def enable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code != 200:
        print(f"[RESTCONF] No loopback{studentID} found on {ip_address}")
        return f"Cannot enable: Interface loopback {studentID}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": True
        }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth,
        headers=headers, 
        verify=False
        )
    if 200 <= resp.status_code <= 299:
        print(f"[RESTCONF] STATUS OK: {resp.status_code}")
        return f"Interface loopback {studentID} is enabled successfully using Restconf"
    else:
        print(f"[RESTCONF] Error. Status Code: {resp.status_code}")
        return f"Cannot enable: Interface loopback {studentID}"


def disable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
    check = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
    if check.status_code != 200:
        print(f"[RESTCONF] No loopback{studentID} found on {ip_address}")
        return f"Cannot shutdown: Interface loopback {studentID}"
    yangConfig = {
        "ietf-interfaces:interface": {
            "enabled": False
        }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if 200 <= resp.status_code <= 299:
        print(f"[RESTCONF] STATUS OK: {resp.status_code}")
        return f"Interface loopback {studentID} is shutdowned successfully using Restconf"
    else:
        print(f"[RESTCONF] Error. Status Code: {resp.status_code}")
        return f"Cannot shutdown: Interface loopback {studentID}"


def status(ip_address):
    api_url_status = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{studentID}"

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface loopback {studentID} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface loopback {studentID} is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface loopback {studentID} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
