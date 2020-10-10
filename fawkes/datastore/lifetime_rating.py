import sys
import os

from pprint import pprint
from datetime import datetime, timedelta

# This is so that the below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.utils.filter_utils as filter_utils
import fawkes.constants.constants as constants
import fawkes.datastore.elasticsearch as elasticsearch

from fawkes.configs.app_config import AppConfig, ReviewChannelTypes
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review
from fawkes.fetch.lifetime import getAppStoreLifetimeRating, getPlayStoreLifetimeRating

def dump_lifetime_ratings(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
    # Read the app-config.json file.
    fawkes_config = FawkesConfig(
        utils.open_json(fawkes_config_file)
    )
    # For every app registered in app-config.json we
    for app_config_file in fawkes_config.apps:
        # Creating an AppConfig object
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
        if app_config.elastic_config.lifetime_rating_index != None:
            time = datetime.strftime(
                datetime.now() - timedelta(1),
                constants.TIMESTAMP_FORMAT
            )

            playstore_rating = getPlayStoreLifetimeRating(app_config)
            appstore_rating = getAppStoreLifetimeRating(app_config)

            # Creating template for uploading lifetime rating
            playstore_doc = Review(
                {},
                timestamp=time,
                rating=playstore_rating,
                app_name=app_config.app.name,
                channel_name="playstore-lifetime",
                channel_type="playstore-lifetime",
                hash_id=utils.calculate_hash(app_config.app.name + ReviewChannelTypes.ANDROID)
            )
            appstore_doc = Review(
                {},
                timestamp=time,
                rating=playstore_rating,
                app_name=app_config.app.name,
                channel_name="appstore-lifetime",
                channel_type="appstore-lifetime",
                hash_id=utils.calculate_hash(app_config.app.name + ReviewChannelTypes.IOS)
            )

            # Deleting document to override
            elasticsearch.delete_document(
                app_config.elastic_config.elastic_search_url,
                app_config.elastic_config.lifetime_rating_index,
                "_doc",
                playstore_doc.hash_id
            )
            elasticsearch.delete_document(
                app_config.elastic_config.elastic_search_url,
                app_config.elastic_config.lifetime_rating_index,
                "_doc",
                appstore_doc.hash_id
            )

            # Uploading again
            elasticsearch.create_document(
                app_config.elastic_config.elastic_search_url,
                app_config.elastic_config.lifetime_rating_index,
                "_doc",
                playstore_doc.hash_id,
                playstore_doc
            )
            elasticsearch.create_document(
                app_config.elastic_config.elastic_search_url,
                app_config.elastic_config.lifetime_rating_index,
                "_doc",
                appstore_doc.hash_id,
                appstore_doc
            )

