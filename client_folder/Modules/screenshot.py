from mss import mss
from mss.tools import to_png


def take_screenshot(client):
    """ Takes a screenshot and sends it to the server. """
    sct = mss()
    img = sct.grab(monitor=sct.monitors[1])
    raw_bytes = to_png(img.rgb, img.size)
    client.send(raw_bytes)
