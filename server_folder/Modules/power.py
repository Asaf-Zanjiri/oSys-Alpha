import config as config
from socket import error as socket_error
import datetime


def restart(server):
    """
    This would restart all of the selected clients.
    :param server: Server socket object
    """
    if datetime.datetime.now() > config.latest_restart_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_restart_time = datetime.datetime.now()
        for target in config.targets:
            config.send_to_client(server, target, 'restart', response=False)
    else:
        print('[!] This command is on cooldown. Please wait additional time')


def shutdown(server):
    """
    This would shutdown all of the selected clients.
    :param server: Server socket object
    """
    if datetime.datetime.now() > config.latest_shutdown_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_shutdown_time = datetime.datetime.now()
        for target in config.targets:
            config.send_to_client(server, target, 'shutdown', response=False)
    else:
        print('[!] This command is on cooldown. Please wait additional time')

# Notes:
# Delete custom console + prints before compiling
