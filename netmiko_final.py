import os
from netmiko import ConnectHandler
from pprint import pprint
from dotenv import load_dotenv
import textfsm
load_dotenv()
device_ip = os.environ.get("ROUTER_IP")
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("sh ip int br", use_textfsm=True)
        # pprint(result)
        for interface in result:
            if interface["interface"].startswith("GigabitEthernet"):
                if interface["status"] == "up":
                    up += 1
                elif interface["status"] == "down":
                    down += 1
                elif interface["status"] == "administratively down":
                    admin_down += 1
                ans += f"{interface['interface']} status: {interface['status']}, "
        ans = ans.rstrip(", ")
        ans += f" -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans


def get_motd(ip):
    device = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": "admin",
        "password": "cisco",
    }

    try:
        with ConnectHandler(**device) as ssh:
            output = ssh.send_command("show banner motd",use_textfsm=True)
            pprint(output)
            # print(output)
            if not output.strip():
                return "Error: No MOTD Configured"
            motd_message = output.strip()
            return motd_message

    except Exception as e:
        return f"Error connecting to {ip}: {e}"
