import datetime
from socket import error as socket_error

# Consts
BUFFER_SIZE = 1024
POWER_MODULE_COOLDOWN = 5
UPDATE_TABLE_COOLDOWN = 3000  # Milliseconds

# Server Variables
client_list = []
targets = []

# Power Module Variables - Cooldowns
latest_restart_time = datetime.datetime(2000, 12, 1, 1, 1)
latest_shutdown_time = datetime.datetime(2000, 12, 1, 1, 1)


def send_to_client(server, target, message, response=True):
    """
    Sends a message to a client
    :param server: Server socket object
    :param target: Target number
    :param message: Message
    :param response: Whether or not the function will wait for a response from the client
    :return: response from the client or None of client lost connection to the server (If receive is enabled)
    """
    try:
        conn = client_list[target]['data']['socket']
        server.send(conn, message)
        if response is True:
            server_response = server.receive(conn)
            if server_response is None:
                delete_client(target)
                return ''
            return server_response
    except socket_error:
        delete_client(target)
        if response is True:
            return ''


def delete_client(target):
    """
    Deletes a target from the client list. Should be used when a client is dead.
    :param target: number of target
    """
    print('[!] Connection was lost..')
    client_list.pop(target)  # Delete dead client from the list
    targets.remove(target)  # Delete dead client from targets list

    # Fix targets list to match new client list.
    for i in range(len(targets)):
        if targets[i] > target:
            targets[i] = targets[i] - 1