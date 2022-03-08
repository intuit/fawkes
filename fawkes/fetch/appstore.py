import requests
import json
import sys
import os
import xmltodict
import logging


# This is so that below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants
import fawkes.constants.logs as logs


def fetch(review_channel):
    reviews = []

    for i in range(review_channel.num_pages_to_fetch):
        # Fetch the app-store reviews
        response = requests.get(
            constants.APP_STORE_RSS_URL.format(
                country=review_channel.country,
                app_id=review_channel.app_id,
                page_number=i + 1,
            )
        )
        # We get an XML reponse, we convert it to json
        review = json.loads(json.dumps(xmltodict.parse(response.text)))
        if "entry" in review["feed"]:
            reviews += review["feed"]["entry"]

    new_reviews = []

    # Correcting the timestamps
    for i in range(len(reviews)):
        try:
            new_review = {
                "updated": reviews[i]["updated"].split("T")[0]
                + " "
                + reviews[i]["updated"].split("T")[1].split("-")[0],
                "rating": int(reviews[i]["im:rating"]),
                "version": reviews[i]["im:version"],
                "content": reviews[i]["content"][0]["#text"],
            }
            new_reviews.append(new_review)
        except BaseException:
            logging.error(logs.APPSTORE_BAD_RESPONSE)

    return new_reviews
