from ncclient import manager
import xmltodict
import os
from dotenv import load_dotenv
load_dotenv()
studentID = os.getenv("STUDENT_ID")
def connect_netconf(ip_address):
    try:
        m = manager.connect(
            host=ip_address,
            port=830,
            username="admin",
            password="cisco",
            hostkey_verify=False
            )
        return m
    except Exception as e:
        print(f"Cannot connect to {ip_address}: {e}")
        return None

def netconf_edit_config(m, netconf_config):
    return m.edit_config(target="running", config=netconf_config)

def create(ip_address):
    m = connect_netconf(ip_address)
    if not m:
        return f"Cannot create: Interface loopback {studentID}"
    check_filter = f"""
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
        </interface>
      </interfaces>
    </filter>
    """
    check = m.get(check_filter)
    if f"Loopback{studentID}" in check.xml:
        return f"Cannot create: Interface loopback {studentID}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
          <description>Loopback interface for {studentID}</description>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is created successfully using Netconf"
        else:
            return f"Cannot create: Interface loopback {studentID}"
    except Exception as e:
        print("Error:", e)
        return f"Cannot create: Interface loopback {studentID}"


def delete(ip_address):
    m = connect_netconf(ip_address)
    if not m:
        return f"Cannot delete: Interface loopback {studentID}"

    # ตรวจว่ามีอยู่ไหม
    check_filter = f"""
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
        </interface>
      </interfaces>
    </filter>
    """
    check = m.get(check_filter)
    if f"Loopback{studentID}" not in check.xml:
        return f"Cannot delete: Interface loopback {studentID}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>Loopback{studentID}</name>
        </interface>
      </interfaces>
    </config>
    """

    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is deleted successfully using Netconf"
        else:
            return f"Cannot delete: Interface loopback {studentID}"
    except Exception as e:
        print("Error:", e)
        return f"Cannot delete: Interface loopback {studentID}"


def enable(ip_address):
    m = connect_netconf(ip_address)
    if not m:
        return f"Cannot enable: Interface loopback {studentID}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is enabled successfully using Netconf"
        else:
            return f"Cannot enable: Interface loopback {studentID}"
    except Exception as e:
        print("Error:", e)
        return f"Cannot enable: Interface loopback {studentID}"

def disable(ip_address):
    m = connect_netconf(ip_address)
    if not m:
        return f"Cannot shutdown: Interface loopback {studentID}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """
    try:
        reply = netconf_edit_config(m, netconf_config)
        if "<ok/>" in reply.xml:
            return f"Interface loopback {studentID} is shutdowned successfully using Netconf"
        else:
            return f"Cannot shutdown: Interface loopback {studentID} (checked by Netconf)"
    except Exception as e:
        print("Error:", e)
        return f"Cannot shutdown: Interface loopback {studentID} (checked by Netconf)"

def status(ip_address):
    m = connect_netconf(ip_address)
    if not m:
        return f"No Interface loopback {studentID} (checked by Netconf)"

    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>Loopback{studentID}</name>
        </interface>
      </interfaces-state>
    </filter>
    """

    try:
        reply = m.get(filter=netconf_filter)
        data = xmltodict.parse(reply.xml)

        interface_data = (
            data.get("rpc-reply", {})
            .get("data", {})
            .get("interfaces-state", {})
            .get("interface")
        )

        if interface_data:
            admin_status = interface_data.get("admin-status")
            oper_status = interface_data.get("oper-status")

            if admin_status == "up" and oper_status == "up":
                return f"Interface loopback {studentID} is enabled (checked by Netconf)"
            elif admin_status == "down" and oper_status == "down":
                return f"Interface loopback {studentID} is disabled (checked by Netconf)"
        else:
            return f"No Interface loopback {studentID} (checked by Netconf)"
    except Exception as e:
        print("Error:", e)
        return f"No Interface loopback {studentID} (checked by Netconf)" 
