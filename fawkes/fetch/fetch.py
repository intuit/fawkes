import json
import sys
import os
import importlib
import pathlib

import appstore
import playstore
import salesforce
import spreadsheet
import tweets
import comma_separated_values

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants as constants

from fawkes.app_config.app_config import AppConfig, ReviewChannelTypes

def fetch_reviews():
    # Read the app-config.json file.
    app_configs = utils.open_json(
        constants.APP_CONFIG_FILE.format(file_name=constants.APP_CONFIG_FILE_NAME)
    )
    # For every app registered in app-config.json we
    for app_config_file in app_configs:
        # Creating an AppConfig object
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
        # Each app has a list of review channels from which the user reviews are fetched.
        for review_channel in app_config.review_channels:
            if review_channel.is_channel_enabled and review_channel.channel_type != ReviewChannelTypes.BLANK:
                # Depending on the channel type, we have different "fetchers" to get the data.
                if review_channel.channel_type == ReviewChannelTypes.TWITTER:
                    reviews = tweets.fetch(
                        review_channel
                    )
                elif review_channel.channel_type == ReviewChannelTypes.SALESFORCE:
                    reviews = salesforce.fetch(
                        review_channel
                    )
                elif review_channel.channel_type == ReviewChannelTypes.SPREADSHEET:
                    reviews = spreadsheet.fetch(
                        review_channel
                    )
                elif review_channel.channel_type == ReviewChannelTypes.CSV:
                    reviews = comma_separated_values.fetch(
                        review_channel
                    )
                elif review_channel.channel_type == ReviewChannelTypes.ANDROID:
                    reviews = playstore.fetch(
                        review_channel
                    )
                elif review_channel.channel_type == ReviewChannelTypes.IOS:
                    reviews = appstore.fetch(
                        review_channel
                    )
                else:
                    continue

                # After fetching the review for that particular channel, we dump it into a file.
                # The file has a particular format.
                # {base_folder}/{dir_name}/{app_name}/{channel_name}-raw-feedback.{extension}
                raw_user_reviews_file_path = constants.RAW_USER_REVIEWS_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.raw_data_folder,
                    app_name=app_config.app.name,
                    channel_name=review_channel.channel_name,
                    extension=review_channel.file_type)

                # Create the intermediate folders
                dir_name = os.path.dirname(raw_user_reviews_file_path)
                pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

                if review_channel.file_type == constants.JSON:
                    utils.dump_json(reviews, raw_user_reviews_file_path)
                else:
                    with open(raw_user_reviews_file_path) as file:
                        file.write(reviews)

        # There are lot of use-cases where we need to execute custom code after the data is fetched.
        # This might include data-transformation, cleanup etc.
        # This is the right place to do that.
        if app_config.custom_code_module_path != None:
            custom_code_module = importlib.import_module(app_config.custom_code_module_path, package=None)
            reviews = custom_code_module.run_custom_code_post_fetch()

if __name__ == "__main__":
    fetch_reviews()
