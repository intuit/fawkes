import sys
import os
import requests

from bs4 import BeautifulSoup

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

from fawkes.configs.app_config import ReviewChannelTypes
from fawkes.review.review import Review

def extract_rating(url, classtype, classname):
    r = requests.get(url)
    soup = ""
    table = ""
    soup = BeautifulSoup(r.content, 'html5lib')
    table = soup.findAll(classtype,
                         attrs={'class': classname})[0].decode_contents()
    return table


def getAppStoreLifetimeRating(app_config):
    ios_channel_config = utils.fetch_channel_config(
        app_config,
        ReviewChannelTypes.IOS
    )
    if ios_channel_config is None:
        return 0.0
    return extract_rating(
        constants.APP_STORE_APP_URL.format(app_id=ios_channel_config.app_id),
        constants.APPSTORE_CLASS_TYPE, constants.APPSTORE_CLASS_NAME)


def getPlayStoreLifetimeRating(app_config):
    android_channel_config = utils.fetch_channel_config(
        app_config,
        ReviewChannelTypes.ANDROID
    )
    if android_channel_config is None:
        return 0.0
    return extract_rating(
        constants.PLAY_STORE_APP_URL.format(app_id=android_channel_config.app_id),
        constants.PLAYSTORE_CLASS_TYPE, constants.PLAYSTORE_CLASS_NAME)
