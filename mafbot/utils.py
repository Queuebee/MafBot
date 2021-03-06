from functools import wraps
import re
from PIL import Image
import math
import operator
import functools
from mafbot import driver
from mafbot.authentication import login


def get(query):
    """ Decorator to retrieve a page and if needed, log in.

    Args:
        query: The query string of the url.
    """

    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            url = 'http://www.maffiaworld.nl' + query
            driver.get(url)

            if 'Inloggen' in driver.title:
                login()

            driver.get(url)
            return f(*args, **kwargs)
        return inner
    return outer


def captcha(f):
    """ Docorator which 'clicks on a captcha to submit an action. """
    @wraps(f)
    def inner(*args, **kwargs):
        f(*args, **kwargs)

        screen_path = '/tmp/screen.png'
        button_path = '/tmp/button.png'

        ref_button = Image.open('button.png')

        # Capture screen and load it.
        driver.get_screenshot_as_file(screen_path)
        screen_img = Image.open(screen_path)

        submit_buttons = driver.find_elements_by_xpath('//td[@class="tcell"]//input[@type="submit"]')

        lowest_rms = ()
        for button in submit_buttons:
            dimensions = (int(button.location['x']), int(button.location['y']), int(button.location['x']) + int(button.size['width']), int(button.location['y']) + int(button.size['height']))
            button_img = screen_img.crop(dimensions)
            button_img.save(button_path)

            # I don't know what this does, exactly,
            # but in the new version ( and tested in py2.7, it doesn't work anymore.)
            rms = math.sqrt(functools.reduce(operator.add,map(lambda a,b: (a-b)**2, ref_button.histogram(), button_img.histogram()))/len(ref_button.histogram()))

            if len(lowest_rms) == 0 or rms < lowest_rms[1]:
                lowest_rms = (button, rms)

        lowest_rms[0].click()
    return inner
