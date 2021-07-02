import config
import datetime


def restart():
    """ This would restart all of the selected clients. """
    if datetime.datetime.now() > config.latest_restart_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_restart_time = datetime.datetime.now()
        for target in config.targets:
            config.log('Restarting client #{}\'s computer'.format(target))
            config.send_to_client(target, 'restart', response=False)
    else:
        config.log('Restarting command is currently on cooldown. Please wait additional time.')


def shutdown():
    """ This would shutdown all of the selected clients. """
    if datetime.datetime.now() > config.latest_shutdown_time + datetime.timedelta(minutes=config.POWER_MODULE_COOLDOWN):
        config.latest_shutdown_time = datetime.datetime.now()
        for target in config.targets:
            config.log('Shutting down client #{}\'s computer'.format(target))
            config.send_to_client(target, 'shutdown', response=False)
    else:
        config.log('Shutdown command is currently on cooldown. Please wait additional time.')
