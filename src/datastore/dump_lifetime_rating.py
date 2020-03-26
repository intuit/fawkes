import sys
import os

from pprint import pprint
from datetime import datetime, timedelta

# This is so that the below import works
sys.path.append(os.path.realpath("."))

from src.fetch_source_data.fetch_lifetime_ratings import *
from src.datastore.dump_data_elasticsearch import *
from src.utils import *
from src.config import *


def get_template(app, rating, channel, hash, time):
    template = {
        "app": app,
        "timestamp": time,
        "message": "",
        "channel-type": channel,
        "properties": {
            "overall-rating": rating,
            "rating": rating
        },
        "derived-insight": {
            "sentiment": {
                "neg": 0.0,
                "neu": 0.0,
                "pos": 0.0,
                "compound": 0.0
            },
            "extra-properties": {
                "bug-feature": "uncategorized"
            },
            "category": "uncategorized"
        },
        "hash-id": hash
    }
    return template


def dump_lifetime_ratings():
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))
    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)
        if LIFETIME_RATING_ELASTICSEARCH_INDEX in app_config.keys():
            time = datetime.strftime(datetime.now() - timedelta(1),
                                     "%Y/%m/%d %H:%M:%S")

            playstore_rating = getPlayStoreLifetimeRating(app_config)
            appstore_rating = getAppStoreLifetimeRating(app_config)

            # Creating template for uploading lifetime rating
            playstore_doc = get_template(
                app_config[APP], playstore_rating, "playstore-lifetime",
                calculate_hash(app_config[APP] + CHANNEL_TYPE_PLAYSTORE), time)
            appstore_doc = get_template(
                app_config[APP], appstore_rating, "appstore-lifetime",
                calculate_hash(app_config[APP] + CHANNEL_TYPE_APPSTORE), time)

            # deleting document to override
            delete_document(app_config[ELASTIC_SEARCH_URL],
                            app_config[LIFETIME_RATING_ELASTICSEARCH_INDEX],
                            "_doc", playstore_doc[HASH_ID])
            delete_document(app_config[ELASTIC_SEARCH_URL],
                            app_config[LIFETIME_RATING_ELASTICSEARCH_INDEX],
                            "_doc", appstore_doc[HASH_ID])

            # Uploading again
            create_document(app_config[ELASTIC_SEARCH_URL],
                            app_config[LIFETIME_RATING_ELASTICSEARCH_INDEX],
                            "_doc", playstore_doc[HASH_ID], playstore_doc)
            create_document(app_config[ELASTIC_SEARCH_URL],
                            app_config[LIFETIME_RATING_ELASTICSEARCH_INDEX],
                            "_doc", appstore_doc[HASH_ID], appstore_doc)


if __name__ == "__main__":
    dump_lifetime_ratings()
