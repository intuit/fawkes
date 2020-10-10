import requests
import json
import sys
import os
import xmltodict

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants


def fetch(review_channel):
    reviews = []

    for i in range(constants.APP_STORE_PAGES_TO_FETCH):
        # Fetch the app-store reviews
        response = requests.get(
            constants.APP_STORE_RSS_URL.format(country=review_channel.country,
                                     app_id=review_channel.app_id,
                                     page_number=i + 1))
        # We get an XML reponse, we convert it to json
        review = json.loads(json.dumps(xmltodict.parse(response.text)))
        if "entry" in review["feed"]:
            reviews += review["feed"]["entry"]

    new_reviews = []

    # Correcting the timestamps
    for i in range(len(reviews)):
        try:
            new_review = {
                "updated":
                    reviews[i]["updated"].split("T")[0] + " " +
                    reviews[i]["updated"].split("T")[1].split("-")[0],
                "rating":
                    int(reviews[i]["im:rating"]),
                "version":
                    reviews[i]["im:version"],
                "content":
                    reviews[i]["content"][0]["#text"],
            }
            new_reviews.append(new_review)
        except BaseException:
            print("[LOG] Parse Error in fetch_app_store_reviews")

    return new_reviews
