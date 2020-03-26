import sys
import os
import requests

from bs4 import BeautifulSoup

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import src.utils as utils

from src.config import *


def extract_rating(url, classtype, classname):
    r = requests.get(url)
    soup = ""
    table = ""
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.findAll(classtype,
                         attrs={'class': classname})[0].decode_contents()
    return table


def getAppStoreLifetimeRating(app_config):
    ios_channel_config = utils.fetch_channel_config(app_config,
                                                    CHANNEL_NAME_APPSTORE)
    if ios_channel_config is None:
        return 0.0
    return extract_rating(
        APP_STORE_APP_URL.format(app_id=ios_channel_config[APP_ID]),
        APPSTORE_CLASS_TYPE, APPSTORE_CLASS_NAME)


def getPlayStoreLifetimeRating(app_config):
    android_channel_config = utils.fetch_channel_config(app_config,
                                                        CHANNEL_NAME_PLAYSTORE)
    if android_channel_config is None:
        return 0.0
    return extract_rating(
        PLAY_STORE_APP_URL.format(app_id=android_channel_config[APP_ID]),
        PLAYSTORE_CLASS_TYPE, PLAYSTORE_CLASS_NAME)
