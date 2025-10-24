import subprocess

def showrun():
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    command = ['ansible-playbook', 'backup-playbook.yaml']
    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout
    print(result)
    if 'ok=2' in result:
        return 'ok'
    else:
        return 'Error: Ansible'
    
def set_motd(message):
    """
    Configure MOTD banner using Ansible playbook.
    """
    command = [
        "ansible-playbook",
        "motd-playbook.yaml",
        "--extra-vars",
        f"motd_message='{message}'"
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
        return "Ok: success"
    else:
        print(result.stderr)
        return f"Error: No MOTD Configured"
