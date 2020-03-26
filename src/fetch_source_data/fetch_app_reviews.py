import requests
import json
import sys
import os

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


def fetch_app_reviews(review_config, app):
    # Since searchman allows us to have limited credits, we iterate over a set of API keys that we will use every month.
    # The API key gets refreshed every month
    searchman_api_key_index = 0
    params = {
        "appId": review_config[APP_ID],
        "apiKey": review_config[SEARCHMAN_API_KEY][searchman_api_key_index],
        "count": 100,
        "start": 0
    }
    reviews = []
    current_page = 0
    while current_page < PLAYSTORE_FETCH_PAGES:
        # I am using try catch because we can't afford to waste the response of the API call.
        # TODO: Remove any such thing from when we directly fetch from play
        # store.
        try:
            params["start"] = current_page * 100
            response = requests.get(SEARCHMAN_REVIEWS_ENDPOINT.format(
                platform=review_config[CHANNEL_TYPE]),
                                    params=params)
            review_page = json.loads(response.text)
            if "data" in review_page:
                review_page = review_page["data"]
                reviews += review_page
                current_page += 1
            else:
                print(
                    "[LOG][ERROR] Bad Response from fetch_app_reviews. Trying next API Key."
                )
                pprint(review_page)
                raise Exception("Bad Response from fetch_app_reviews")
        except BaseException:
            searchman_api_key_index += 1
            if searchman_api_key_index < len(review_config[SEARCHMAN_API_KEY]):
                params["apiKey"] = review_config[SEARCHMAN_API_KEY][
                    searchman_api_key_index]
            else:
                print("[LOG][ERROR] Exhausted all API keys")
                break

    dir = DATA_DUMP_DIR

    fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
        dir_name=dir,
        app_name=app,
        channel_name=review_config[CHANNEL_NAME],
        extension="json")

    if not os.path.exists(dir):
        os.makedirs(dir)
    # TODO Fix for pagination
    dump_json(reviews, fetch_file_save_path)
