import sys
import os
import json
import csv
import importlib
import pathlib

from pytz import timezone
from pprint import pprint

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

from fawkes.configs.app_config import AppConfig, ReviewChannelTypes
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review

def parse_csv(raw_user_reviews_file_path, review_channel, app_config):
    """ Parses the CSV files to a Review object """

    with open(raw_user_reviews_file_path, "r") as file_handle:
        # Read all the reviews from the CSV file
        reviews = csv.reader(file_handle, delimiter=",")

        # We expect the first row to contain the column names.
        # TODO: We should change this to be taken from the configuration.
        # There might be usecases where column names are not present in the data.
        # People might want to indicate the message, timestamp keys using integer indices to the columns.
        json_keys_list = reviews[0]
        parsed_reviews = []

        # Removing the first row.
        reviews = reviews[1:]

        # Iterate through all the reviews
        for row in reviews:
            review = {}
            timestamp = ""
            message = ""
            rating = None

            # There are some csvs for which the last column is empty.
            # Hence we need to take the min below
            for i in range(min(len(json_keys_list), len(row))):
                if json_keys_list[i] == review_channel.timestamp_key:
                    # Storing the timestamp
                    timestamp = row[i]
                elif json_keys_list[i] == review_channel.message_key:
                    # Storing the message
                    message = row[i]
                elif json_keys_list[i] == review_channel.rating_key:
                    rating = row[i]
                # Storing the raw review as received from the source.
                review[json_keys_list[i]] = row[i]

            # Add the review object to the parsed reviews
            parsed_reviews.append(
                Review(
                    review,
                    message=message,
                    timestamp=timestamp,
                    rating=rating,
                    app_name=app_config.app.name,
                    channel_name=review_channel.channel_name,
                    channel_type=review_channel.channel_type,
                )
            )

    return parsed_reviews


def parse_json(raw_user_reviews_file_path, review_channel, app_config):
    """ Parses the JSON files to a Review object """

    reviews = utils.open_json(raw_user_reviews_file_path)
    parsed_reviews = []

    for review in reviews:
        # TODO: Conver this to a standard format like jsonpath.
        # Extract the message.
        message = utils.get_json_key_value(review, review_channel.message_key.split("."))
        # Extract the timestamp.
        timestamp = utils.get_json_key_value(review, review_channel.timestamp_key.split("."))
        # Extract the rating if present.
        rating = None
        if review_channel.rating_key != None:
            rating = utils.get_json_key_value(review, review_channel.rating_key.split("."))

        # Add the review object to the parsed reviews
        parsed_reviews.append(
            Review(
                review,
                message=message,
                timestamp=timestamp,
                rating=rating,
                app_name=app_config.app.name,
                channel_name=review_channel.channel_name,
                channel_type=review_channel.channel_type,
                review_timezone=review_channel.timezone,
                timestamp_format=review_channel.timestamp_format,
            )
        )

    return parsed_reviews

def parse_json_lines(raw_user_reviews_file_path, review_channel, app_config):
    parsed_reviews = []
    with open(raw_user_reviews_file_path, "r") as raw_user_reviews_file_handle:
        # We read the file line by line as each line is a valid json string. https://jsonlines.org/
        for line in raw_user_reviews_file_handle:
            review = json.loads(line)
            # TODO: Conver this to a standard format like jsonpath.
            # Extract the message.
            message = utils.get_json_key_value(review, review_channel.message_key.split("."))
            # Extract the timestamp.
            timestamp = utils.get_json_key_value(review, review_channel.timestamp_key.split("."))
            # Extract the rating if present.
            rating = None
            if review_channel.rating_key != None:
                rating = utils.get_json_key_value(review, review_channel.rating_key.split("."))

            # Add the review object to the parsed reviews
            parsed_reviews.append(
                Review(
                    review,
                    message=message,
                    timestamp=timestamp,
                    rating=rating,
                    app_name=app_config.app.name,
                    channel_name=review_channel.channel_name,
                    channel_type=review_channel.channel_type,
                    review_timezone=review_channel.timezone,
                    timestamp_format=review_channel.timestamp_format,
                )
            )
    return parsed_reviews

def parse_reviews(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
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
        parsed_reviews = []
        # We now read the review details for each channel
        for review_channel in app_config.review_channels:
            # We parse the channels only if its enabled!
            if review_channel.is_channel_enabled and review_channel.channel_type != ReviewChannelTypes.BLANK:
                raw_user_reviews_file_path = constants.RAW_USER_REVIEWS_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.raw_data_folder,
                    app_name=app_config.app.name,
                    channel_name=review_channel.channel_name,
                    extension=review_channel.file_type
                )
                if review_channel.file_type == constants.JSON: # Parse JSON
                    channel_reviews = parse_json(
                        raw_user_reviews_file_path,
                        review_channel, app_config
                    )
                elif review_channel.file_type == constants.CSV: # Parse CSV
                    channel_reviews = parse_csv(
                        raw_user_reviews_file_path,
                        review_channel,
                        app_config
                    )
                elif review_channel.file_type == constants.JSON_LINES:
                    channel_reviews = parse_json_lines(
                        raw_user_reviews_file_path,
                        review_channel,
                        app_config
                    )
                else: # Unsupported file format
                    raise (
                        "Format not supported exception. Check your file-type key in your config."
                    )
                parsed_reviews += channel_reviews

        # Executing custom code after parsing.
        if app_config.custom_code_module_path != None:
            custom_code_module = importlib.import_module(app_config.custom_code_module_path, package=None)
            parsed_reviews = custom_code_module.run_custom_code_post_parse(
                parsed_reviews)

        # After parsing the reviews for that all channels, we dump it into a file.
        # The file has a particular format.
        # {base_folder}/{dir_name}/{app_name}/parsed-user-feedback.{extension}
        parsed_user_reviews_file_path = constants.PARSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.parsed_data_folder,
            app_name=app_config.app.name,
        )

        # Create the intermediate folders
        dir_name = os.path.dirname(parsed_user_reviews_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        utils.dump_json(
            [parsed_review.to_dict() for parsed_review in parsed_reviews],
            parsed_user_reviews_file_path
        )
