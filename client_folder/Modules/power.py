from os import system


def restart():
    """ Restarts the pc """
    system('shutdown /r /t 0')


def shutdown():
    """ Powers off the pc """
    system("shutdown /s /t 0")
