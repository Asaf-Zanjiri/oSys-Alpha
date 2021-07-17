from zlib import compress, decompress
from gui import start as start_gui
from threading import Thread
from datetime import datetime
from time import sleep
import config
import socket
import sys


class Server:
    def __init__(self, ip, port):
        """
        Initiates the server
        :param ip: ip address to host the server on
        :param port: port to listen for connections on
        """
        config.log('Starting server on {}:{} ...'.format(ip, port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        config.log('Listening for clients...')

    def close(self):
        """ Closes the server """
        self.server_socket.close()

    @staticmethod
    def send(sock, message):
        """
        Sends a message in small chunks to the client
        :param sock: Client socket object
        :param message: Message to send to the server (bytes/str)
        """
        message = message.encode() if type(message) != bytes else message
        message = compress(message, level=6)  # Compress the sent data
        if len(message) % config.BUFFER_SIZE == 0:
            message = message + '.'.encode()
        while message:
            sock.send(message[:config.BUFFER_SIZE])
            message = message[config.BUFFER_SIZE:]

    @staticmethod
    def receive(sock, as_bytes=False):
        """
        Receive a message in small chunks from the client
        :param sock: Client socket object
        :param as_bytes: If set to True, this function will return the data as bytes. Default=False
        """
        chunk = sock.recv(config.BUFFER_SIZE)
        data = chunk
        while len(chunk) == config.BUFFER_SIZE:
            chunk = sock.recv(config.BUFFER_SIZE)
            sleep(0.001)  # To avoid receive overlap. A bit scuffed solution but it works.
            if chunk != '.'.encode():
                data += chunk

        data = decompress(data)  # Decompress the received data
        return data if as_bytes else data.decode(errors="ignore")

    def client_connections(self):
        """ Handles new connections and adds them to the client list. """
        try:
            while True:
                (client_socket, addr) = self.server_socket.accept()
                config.log('New connection from: ' + str(addr[0]))
                client_data = self.receive(client_socket).split(',')  # IP,CountryCode,Name,OS

                # Add new client to the clients list
                exist = False
                for client in config.client_list:
                    if client['ip'] == addr[0]:
                        exist = True
                        break
                if not exist:
                    config.client_list.append({'ip': client_data[0], 'data': {'countryCode': client_data[1], 'name': client_data[2], 'os': client_data[3], 'socket': client_socket, 'last_screenshot_time': datetime(2000, 12, 1, 1, 1)}})
        except socket.error as e:
            config.log('Error: ' + str(e))
            self.client_connections()


def main():
    # Default Server Parameters
    ip = 'localhost'
    port = 8000

    # Change IP and Port according to the startup args
    for arg in sys.argv[1:]:
        if arg.startswith('--ip=') or arg.startswith('-i='):
            ip_arg = arg.split('=', maxsplit=1)[1]
            print(ip_arg)
            if ip_arg != '':
                ip = ip_arg
            else:
                config.log('Invalid ip address was inputted.')
        elif arg.startswith('--port=') or arg.startswith('-p='):
            try:
                port = int(arg.split('=', maxsplit=1)[1])
            except ValueError as e:
                config.log(str(e))
                config.log('Inputted port number is invalid. Starting on default port')

    # Start server
    try:
        config.SERVER = Server(ip, port)  # Initiates the server
        Thread(target=config.SERVER.client_connections, daemon=True).start()  # Thread to accept new connections
        start_gui()  # Start the GUI
    except socket.gaierror as e:
        config.log(str(e))
        config.log('Invalid IP address to host server on.')
    except OverflowError as e:
        config.log(str(e))
        config.log('Invalid Port number to host server on.')


if __name__ == "__main__":
    main()
