import subprocess

def showrun(device_ip):
    command = [
        'ansible-playbook',
        'backup-playbook.yaml',
        '-e', f"router_ip={device_ip}"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if 'ok=4' in result.stdout:
        return 'ok'
    else:
        return 'Error: Ansible'
    
import subprocess

def set_motd(ip_address, message):
    """
    Configure MOTD banner on a specific router using Ansible playbook.
    """
    command = [
        "ansible-playbook",
        "motd-playbook.yaml",
        "--extra-vars",
        f"router_ip={ip_address} motd_message=\"{message}\""
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return "Ok: success"
    else:
        print(result.stderr)
        return "Error: No MOTD Configured"