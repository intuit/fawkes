import json
import sys
import os
import importlib

from shutil import copyfile
from fetch_app_store_reviews import *
from fetch_app_reviews import *
from fetch_salesforce_review import *
from fetch_spreadsheet_review import *
from fetch_twitter_data import *

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


def fetch_csv(review_details, app_name):
    fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
        dir_name=DATA_DUMP_DIR,
        app_name=app_name,
        channel_name=review_details[CHANNEL_NAME],
        extension="csv")
    copyfile(review_details[FILE_PATH], fetch_file_save_path)


def fetch_reviews():
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    app_json_schema = open_json("src/app-config-schema.json")

    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)

        for review_details in app_config[REVIEW_CHANNELS]:
            if review_details[IS_CHANNEL_ENABLED] and review_details[
                    CHANNEL_TYPE] != BLANK:
                print("[LOG]:: fetching...", app, review_details[CHANNEL_TYPE],
                      review_details[CHANNEL_NAME])
                if review_details[CHANNEL_TYPE] == CHANNEL_TYPE_TWITTER:
                    fetch_from_twitter(review_details, app_config[APP])

                elif review_details[CHANNEL_TYPE] == CHANNEL_TYPE_SALESFORCE:
                    fetch_from_salesforce(review_details, app_config[APP])

                elif review_details[CHANNEL_TYPE] == CHANNEL_TYPE_SPREADSHEET:
                    fetch_review_from_spreadsheet(review_details,
                                                  app_config[APP])

                elif review_details[CHANNEL_TYPE] == CHANNEL_TYPE_CSV:
                    fetch_csv(review_details, app_config[APP])

                elif review_details[CHANNEL_TYPE] == CHANNEL_TYPE_PLAYSTORE:
                    fetch_app_reviews(review_details, app_config[APP])

                elif review_details[CHANNEL_TYPE] == CHANNEL_TYPE_APPSTORE:
                    fetch_app_store_reviews(review_details, app_config[APP])
                else:
                    continue
        # Executing custom code after parsing.
        if CUSTOM_CODE_PATH in app_config:
            custom_code_module = importlib.import_module(
                APP + "." + app_config[CUSTOM_CODE_PATH], package=None)
            reviews = custom_code_module.run_custom_code_post_fetch()


if __name__ == "__main__":
    fetch_reviews()
