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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot create: Interface loopback {studentID}"

def delete(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
    resp = requests.delete(
        api_url, 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot delete: Interface loopback {studentID}"


def enable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot enable: Interface loopback {studentID}"


def disable(ip_address):
    api_url = f"https://{ip_address}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{studentID}"
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

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
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
            return f"Interface loopback {studentID} is enabled using Restconf"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface loopback {studentID} is disabled using Restconf"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface loopback {studentID}"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
