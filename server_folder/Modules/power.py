import config


def restart():
    """ This would restart all of the selected clients. """
    for target in config.targets:
        config.log('Restarting client #{}\'s computer'.format(target))
        config.send_to_client(target, 'restart', response=False)


def shutdown():
    """ This would shutdown all of the selected clients. """
    for target in config.targets:
        config.log('Shutting down client #{}\'s computer'.format(target))
        config.send_to_client(target, 'shutdown', response=False)
