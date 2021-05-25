import os


def restart():
    """ Restarts the pc """
    os.system('shutdown /r /t 0')


def shutdown():
    """ Powers off the pc """
    os.system("shutdown /s /t 0")
