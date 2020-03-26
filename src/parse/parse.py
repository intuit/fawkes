import sys
import os
import json
import csv
import importlib

from pytz import timezone
from pprint import pprint

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


def convert_keys_to_lower(reviews):
    """ Converts all the keys to lower case """
    for review in reviews:
        d = {}
        for key in review["properties"]:
            key_lower = key.lower()
            d[key_lower] = review["properties"][key]
        review["properties"] = d
    return reviews


def add_and_convert_timezone(review, review_config):
    try:
        review[TIMESTAMP] = datetime.strptime(review[TIMESTAMP],
                                              "%Y/%m/%d %H:%M:%S")
        review[TIMESTAMP] = review[TIMESTAMP].replace(
            tzinfo=timezone(review_config[TIMEZONE]))
        review[TIMESTAMP] = review[TIMESTAMP].astimezone(timezone('UTC'))
        review[TIMESTAMP] = review[TIMESTAMP].strftime("%Y/%m/%d %H:%M:%S")
    except BaseException:
        print("[LOG] Exception in add_and_convert_timezone :: ",
              review[TIMESTAMP])
    return review


def post_parsing(reviews, review_config):
    """ Channel specific parsing """
    new_reviews = reviews

    # We remove the tweets that are not authentic
    if review_config[CHANNEL_TYPE] == CHANNEL_TYPE_TWITTER and review_config[
            TWITTER_HANDLE_BALCKLIST]:
        new_reviews = [
            review for review in reviews if check_tweet_authenticity(
                review[MESSAGE], review_config[TWITTER_HANDLE_BALCKLIST])
            and check_for_explicit_content(review[PROPERTIES])
        ]

    new_reviews = [
        add_and_convert_timezone(review, review_config)
        for review in new_reviews
    ]

    return new_reviews


def parse_csv(channel_data_path, review_config, app_config):
    """
    Parses csv files and created unofied json
    Format of parsed json :
        app : app-type
        timestamp : "2015/01/01 12:10:30", (this format only coz elastic search identifies date field only if this format only)
        message : "feedback / REVIEW"
        channel-type : "channel"
        properties : {
            contains data from original source for each channel.
        }

    """

    with open(channel_data_path, "r") as file_handle:
        reviews = csv.reader(file_handle, delimiter=",")
        first_row_not_parsed = True
        parsed_reviews = []

        for row in reviews:
            # Take column names as json keys
            if first_row_not_parsed:
                json_keys_list = row
                first_row_not_parsed = False
                continue

            record = {}
            timestamp = ""
            message = ""

            # Some csvs for which the last column is empty.
            for i in range(min(len(json_keys_list), len(row))):
                if json_keys_list[i] == review_config[TIMESTAMP_KEY]:
                    timestamp = convert_date_format(row[i])
                elif json_keys_list[i] == review_config[MESSAGE_KEY]:
                    message = generic_cleanup(remove_links(row[i]))
                record[json_keys_list[i]] = generic_cleanup(row[i])

            parsed_reviews.append(
                format_input_json(app_config[APP], timestamp, message,
                                  review_config[CHANNEL_NAME], record))
    return parsed_reviews


def parse_json(channel_data_path, review_config, app_config):
    """ Parses json file types and creates unified json """

    reviews = open_json(channel_data_path)
    parsed_reviews = []
    for review in reviews:
        # Clean up message. sorry for telling to write it in single line.
        message = get_json_key_value(review,
                                     review_config[MESSAGE_KEY].split("."))
        if message is None:
            message = ""
        message = remove_links(message)
        message = generic_cleanup(message)
        timestamp = convert_date_format(
            get_json_key_value(review, review_config[TIMESTAMP_KEY].split(".")))
        formatted_json = format_input_json(app_config[APP], timestamp, message,
                                           review_config[CHANNEL_NAME], review)
        parsed_reviews.append(formatted_json)
    return parsed_reviews


def parse_reviews():
    # Read all the app-config file names
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    for app in app_configs:
        print("[LOG] Parsing app : ", app)
        parsed_review = []
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)
        # We now read the review details for each channel
        for review_config in app_config[REVIEW_CHANNELS]:
            # We parse the channels only if its enabled!
            if review_config[IS_CHANNEL_ENABLED] and review_config[
                    CHANNEL_TYPE] != BLANK:
                print("[LOG] Parsing channel : ", review_config[CHANNEL_NAME])

                channel_data_path = FETCH_FILE_SAVE_PATH.format(
                    dir_name=DATA_DUMP_DIR,
                    app_name=app_config[APP],
                    channel_name=review_config[CHANNEL_NAME],
                    extension=review_config[FILE_TYPE])

                if review_config[FILE_TYPE] == "json":
                    channel_review = parse_json(channel_data_path,
                                                review_config, app_config)
                elif review_config[FILE_TYPE] == "csv":
                    channel_review = parse_csv(channel_data_path, review_config,
                                               app_config)
                else:
                    raise (
                        "Format not supported exception. Check your file-type key in your config."
                    )
                channel_review = post_parsing(channel_review, review_config)
                parsed_review += channel_review

        # Executing custom code after parsing.
        if CUSTOM_CODE_PATH in app_config:
            custom_code_module = importlib.import_module(
                APP + "." + app_config[CUSTOM_CODE_PATH], package=None)
            parsed_review = custom_code_module.run_custom_code_post_parse(
                parsed_review)

        parsed_reviews = convert_keys_to_lower(parsed_review)

        if not os.path.exists(PROCESSED_DATA_DIR):
            os.makedirs(PROCESSED_DATA_DIR)

        dump_json(
            parsed_reviews,
            PARSED_INTEGRATED_REVIEW_FILE.format(app_name=app_config[APP]))


if __name__ == "__main__":
    parse_reviews()
