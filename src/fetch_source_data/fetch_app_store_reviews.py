import requests
import json
import sys
import os
import xmltodict

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


def fetch_app_store_reviews(review_config, app):
    reviews = []
    for i in range(APP_STORE_PAGES_TO_FETCH):
        # Fetch the app-store reviews
        response = requests.get(
            APP_STORE_RSS_URL.format(country=review_config[COUNTRY],
                                     app_id=review_config[APP_ID],
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

    dir = DATA_DUMP_DIR

    if not os.path.exists(dir):
        os.makedirs(dir)

    fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
        dir_name=dir,
        app_name=app,
        channel_name=review_config[CHANNEL_NAME],
        extension="json")

    dump_json(new_reviews, fetch_file_save_path)
