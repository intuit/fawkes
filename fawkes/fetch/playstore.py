import requests
import json
import sys
import os

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

def fetch(review_channel):
    # Since searchman allows us to have limited credits, we iterate over a set of API keys that we will use every month.
    # The API key gets refreshed every month
    searchman_api_key_index = 0
    params = {
        "appId": review_channel.app_id,
        "apiKey": review_channel.searchman_api_key[searchman_api_key_index],
        "count": 100,
        "start": 0
    }

    reviews = []
    current_page = 0

    while current_page < constants.PLAYSTORE_FETCH_PAGES:
        # I am using try catch because we can't afford to waste the response of the API call.
        # TODO: Remove any such thing from when we directly fetch from play
        # store.
        try:
            params["start"] = current_page * 100
            response = requests.get(constants.SEARCHMAN_REVIEWS_ENDPOINT.format(
                platform=review_channel.channel_type),
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
                raise Exception("Bad Response from fetch_app_reviews")
        except BaseException:
            searchman_api_key_index += 1
            if searchman_api_key_index < len(review_channel.searchman_api_key):
                params["apiKey"] = review_channel.searchman_api_key[
                    searchman_api_key_index]
            else:
                print("[LOG][ERROR] Exhausted all API keys")
                break

    return reviews
