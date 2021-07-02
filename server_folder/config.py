import datetime
from socket import error as socket_error

# Consts
BUFFER_SIZE = 1024
POWER_MODULE_COOLDOWN = 5
UPDATE_TABLE_COOLDOWN = 3000  # Milliseconds
SERVER = None

# Server Variables
client_list = []
targets = []

# Power Module Variables - Cooldowns
latest_restart_time = datetime.datetime(2000, 12, 1, 1, 1)
latest_shutdown_time = datetime.datetime(2000, 12, 1, 1, 1)


def send_to_client(target, message, response=True):
    """
    Sends a message to a client
    :param target: Number of client
    :param message: Message
    :param response: Whether or not the function will wait for a response from the client
    :return: response from the client or None of client lost connection to the server (If receive is enabled)
    """
    try:
        conn = client_list[target]['data']['socket']
        SERVER.send(conn, message)
        if response is True:
            server_response = SERVER.receive(conn)
            if server_response is None:
                delete_client(target)
                return ''
            return server_response
    except socket_error as e:
        log('Error: ' + str(e))
        delete_client(target)
        if response is True:
            return ''


def delete_client(target):
    """
    Deletes a target from the client list. Should be used when a client is dead.
    :param target: Number of client
    """
    log('Connection to client #{} was lost... Removing client...'.format(target+1))
    client_list.pop(target)  # Delete dead client from the list
    targets.remove(target)  # Delete dead client from targets list

    # Fix targets list to match new client list.
    for i in range(len(targets)):
        if targets[i] > target:
            targets[i] = targets[i] - 1


def log(message):
    """
    Logs a message to a log file in the server folder.
    :param message: Message to log
    """
    with open('oSys-{}.log'.format(datetime.datetime.now().strftime('%d.%m.%Y')), 'a+') as f:
        f.write(datetime.datetime.now().strftime('[%d/%m/%Y %H:%M:%S]: ') + message + '\n')
        print('--------------------\n', message)
