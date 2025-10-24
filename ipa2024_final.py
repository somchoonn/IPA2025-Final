#######################################################################################
# Yourname: Chanokchon Pancome
# Your student ID: 66070247
# Your GitHub Repo: https://github.com/somchoonn/IPA2025-Final
#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.
import os,json,time
import requests
import glob
from requests_toolbelt.multipart.encoder import MultipartEncoder    
from restconf_final import create as rc_create, delete as rc_delete, enable as rc_enable, disable as rc_disable, status as rc_status
from netconf_final  import create as nc_create, delete as nc_delete, enable as nc_enable, disable as nc_disable, status as nc_status

from netmiko_final import gigabit_status,get_motd
from ansible_final import showrun,set_motd
from dotenv import load_dotenv
load_dotenv()
#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
student_id = os.environ.get("STUDENT_ID")
ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")

current_method = None
allowed_ips = os.getenv("ALLOWED_IPS", "").split(",")
allowed_ips = [ip.strip() for ip in allowed_ips if ip.strip()]
#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID")

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    if message.startswith(f"/{student_id}"):
        parts = message.split()
        ipOrMethod = parts[1].strip()
        command = parts[2].strip() if len(parts) > 2 else None #for index out of range
        
        #Check Method
        if ipOrMethod.lower() == "restconf" or ipOrMethod.lower() == "netconf":
            current_method = ipOrMethod.lower()
            responseMessage = f"Ok: {current_method.capitalize()}"
        
        #MOTD
        elif len(parts) >= 3 and command == "motd":
            ip_address = ipOrMethod
            if ip_address not in allowed_ips:
                responseMessage = "Error: IP address not allowed"
            else:
                # ถ้ามีข้อความตามหลัง (ตั้งค่า)
                if len(parts) > 3:
                    motd_text = " ".join(parts[3:])
                    responseMessage = set_motd(motd_text)
                else:
                # ถ้าไม่มีข้อความ (อ่านค่า)
                    responseMessage = get_motd(ip_address)
        #Check No IP /66070247 Create 
        elif ipOrMethod.lower() in ["create", "delete", "enable", "disable", "status"]:
            if current_method is None:
                responseMessage = "Error: No method specified"
            else:
                responseMessage = "Error: No IP specified"
            
        #Check No command /66070247 [IP]
        elif len(parts) == 2 and ipOrMethod in allowed_ips:
            responseMessage = "Error: No command found."
        #Check No IP /66070247 [commands]
        elif ipOrMethod.lower() in ["create", "delete", "enable", "disable", "status"]:
            if current_method is None:
                responseMessage = "Error: No method specified"
            else:
                responseMessage = "Error: No IP specified"
        #Check IP Command /66070247 [allowed IPs] [command]
        elif len(parts) >= 3:
            ip_address = ipOrMethod
            if current_method is None:
                responseMessage = "Error: No method specified"
            else:
                if current_method == "restconf":
                    if ip_address not in allowed_ips:
                        responseMessage = "Error: IP address not allowed"
                    else:
                        if command in ["create", "delete", "enable", "disable", "status"]:
                            # CALL RESTCONF FUNCTIONS
                            if command == "create":
                                responseMessage = rc_create(ip_address)
                            elif command == "delete":
                                responseMessage = rc_delete(ip_address)
                            elif command == "enable":
                                responseMessage = rc_enable(ip_address)
                            elif command == "disable":
                                responseMessage = rc_disable(ip_address)
                            elif command == "status":
                                responseMessage = rc_status(ip_address)
                elif current_method == "netconf":
                    if ip_address not in allowed_ips:
                        responseMessage = "Error: IP address not allowed"
                    else:
                        if command in ["create", "delete", "enable", "disable", "status"]:
                            # CALL RESTCONF FUNCTIONS
                            if command == "create":
                                responseMessage = nc_create(ip_address)
                            elif command == "delete":
                                responseMessage = nc_delete(ip_address)
                            elif command == "enable":
                                responseMessage = nc_enable(ip_address)
                            elif command == "disable":
                                responseMessage = nc_disable(ip_address)
                            elif command == "status":
                                responseMessage = nc_status(ip_address)
        elif ipOrMethod == "gigabit_status":
            responseMessage = gigabit_status()
        elif ipOrMethod == "showrun":
            responseMessage = showrun()
        else:
            responseMessage = "Error: No command or unknown command"

        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if ipOrMethod == "showrun" and responseMessage == 'ok':
            filename = f"show_run_{student_id}_R1-Exam.txt"
            fileobject = open(filename, "rb")  
            filetype = "text/plain"
            postData = {
                "roomId": roomIdToGetMessages,
                "text": f"show running config of {student_id}",
                "files": (filename, fileobject, filetype),
            }
            postData = MultipartEncoder(postData)
            HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": postData.content_type,
            }
        # other commands only send text, or no attached file.
        else:
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
