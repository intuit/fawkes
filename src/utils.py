import json
import ast
import sys
import os
import re
import csv
import itertools
import operator
import dateutil.parser
import hashlib

import gensim
import spacy
import jsonschema

from datetime import datetime
from pprint import pprint
from datetime import datetime, timedelta

from gensim.utils import simple_preprocess
from nltk.corpus import stopwords

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

from src.stop_words_file import *
from src.config import *


def open_json(file_location):
    with open(file_location, "r") as read_file:
        documents = json.load(read_file)
    return documents


def dump_json(records, write_file):
    with open(write_file, "w") as file:
        json.dump(records, file, indent=4)


def merge_json(file1, file2):
    """ Merges two jsons which are list of dictionaries """
    first_part = open_json(file1)
    second_part = open_json(file2)
    merged_contents = first_part + second_part

    return merged_contents


def remove_links(message):
    return re.sub(LINK_REGEX, "", message)


def convert_keys_to_lower(reviews):
    for review in reviews:
        d = {}
        for key in review[PROPERTIES]:
            key_lower = key.lower()
            d[key_lower] = review[PROPERTIES][key]
        review[PROPERTIES] = d
    return reviews


def get_json_key_value(json_object, keys_list):
    """ Get the value from json pointing to string of keys input: [k1,k2] """
    # This will be the key
    key = keys_list[0]

    # We check for types, if its a dict or list
    if isinstance(json_object, list):
        key = int(key)
        # Check for index out of range
        if key >= len(json_object):
            return None

    if len(keys_list) == 1:
        # We first check if its a list and then move forward.
        # Think, why we did it like that ?
        if isinstance(json_object, list):
            return json_object[key]
        elif key in json_object:
            return json_object[key]
        else:
            return None

    return get_json_key_value(json_object[key], keys_list[1:])


def format_input_json(app, timestamp, message, channel_type, properties):
    """
    Returns formatted parsed data.
    Format of parsed json :
        app : app_name
        timestamp : "2015/01/01 12:10:30", (this format only coz elastic search identifies date field only if this format only)
        message : "feedback / REVIEW"
        channel-type : "channel"
        properties : {
            rating : 3
            contains rest of the channel specific data.
        }
    """
    parsed_data = {}
    parsed_data[APP] = app
    parsed_data[TIMESTAMP] = timestamp
    parsed_data[MESSAGE] = message
    parsed_data[CHANNEL_TYPE] = channel_type
    parsed_data[PROPERTIES] = properties
    parsed_data[HASH_ID] = calculate_hash(timestamp + message)

    return parsed_data


def convert_date_format(dateformat):
    """
    Identifies most date time formats and converts them into unified date times format:
        YYYY/MM/DD HH:MM:SS
    Elastic Search identifies this format only.
    """

    # Converts both unix and general time formats
    try:
        yourdate = dateutil.parser.parse(dateformat)
    except BaseException:
        try:
            return datetime.utcfromtimestamp(
                float(dateformat)).strftime("%Y/%m/%d %H:%M:%S")
        except BaseException:
            return ""

    oldformat = str(yourdate)
    datetimeobject = datetime.strptime(oldformat, '%Y-%m-%d  %H:%M:%S')
    newformat = datetimeobject.strftime('%Y/%m/%d %H:%M:%S')

    return newformat


def generic_cleanup(message):
    """
    All the parsing codes call this for generic cleanup.
    """

    # Important to have quotes for sentiment to be correctly identified
    message = message.replace(u"\u2018", "'")
    message = message.replace(u"\u2019", "'")

    message = message.replace("\n", "")
    message = message.replace("\t", "")
    # Removes links from message using regex
    regex = re.compile(URL_REGEX)
    message = regex.sub("", message)

    # Removing the non ascii chars
    message = (message.encode("ascii", "ignore")).decode("utf-8")

    return message


def check_tweet_authenticity(tweet_message, twitter_handle_blacklist):
    """  Checks if tweets incoming are authentic. basically there is blacklist of twitter-handles """
    is_tweet_authentic = True

    for handle in twitter_handle_blacklist:
        if handle in tweet_message:
            is_tweet_authentic = False

    return is_tweet_authentic


def check_for_explicit_content(tweet):
    if POSSIBLY_SENSITIVE in tweet:
        return tweet[POSSIBLY_SENSITIVE]
    return True


def format_output_json(input_dict,
                       category=None,
                       sentiment=None,
                       derived_insight_properties=None):
    """ Creates the json according to the unified json output format """
    temp_dict = {}

    # If the node that we are already passing has an insight, we write over it.
    if DERIVED_INSIGHTS in input_dict:
        temp_dict = input_dict[DERIVED_INSIGHTS]

    if derived_insight_properties is not None:
        if EXTRA_PROPERTIES in temp_dict:
            temp_dict[EXTRA_PROPERTIES] = {
                **temp_dict[EXTRA_PROPERTIES],
                **derived_insight_properties
            }
        else:
            temp_dict[EXTRA_PROPERTIES] = derived_insight_properties

    # Touch the category only if you know what you are doing! You Moron!
    if category is not None:
        temp_dict[CATEGORY] = category

    # Do not play with my sentiments! You Moron!
    if sentiment is not None:
        temp_dict[SENTIMENT] = sentiment

    input_dict[DERIVED_INSIGHTS] = temp_dict

    return input_dict


def remove_duplicates(list_with_duplicates):
    clean_list = []
    for doc in list_with_duplicates:
        message_list = [sent[MESSAGE] for sent in clean_list]
        if doc[MESSAGE] not in message_list:
            clean_list.append(doc)
    return clean_list


#


def filter_review_on_channel(channel_list, reviews):
    """ Filters the review for those channels which are not in channel_list """
    return [
        review for review in reviews if review[CHANNEL_TYPE] in channel_list
    ]


def filter_review_on_time(reviews, from_date):
    return [
        review for review in reviews if review[TIMESTAMP] != "" and
        datetime.strptime(review[TIMESTAMP], '%Y/%m/%d %H:%M:%S') > from_date
    ]


def tokenise(document):
    return gensim.utils.simple_preprocess(str(document), deacc=True)


def remove_stop_words(document):
    """
        Removes stop words. Takes tokenised document as input and returns
        after removing the stop words.
        input : ["phil","is","good"]
        output : ["phil","good"]
    """

    stop_words = stopwords.words("english")
    stop_words = set(stop_words + EXTENDED_STOP_WORDS)
    return [token for token in document if token not in stop_words]


def lemmatisation(text, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    """
    Does lemmatisation. whats lemmatisation? google :P
    Input : ["phil", "is", "good"]
    - https://spacy.io/api/annotation
    - https://spacy.io/api/top-level
    """
    nlp = spacy.load("en", disable=["parser", "ner"])
    doc = nlp(" ".join(text))
    return [token.lemma_ for token in doc if token.pos_ in allowed_postags]


def get_positive_review(reviews):
    return [
        review for review in reviews
        if review[DERIVED_INSIGHTS][SENTIMENT]["compound"] > 0.0
    ]


def get_negative_review(reviews):
    """ Why does positive come above negative?? Think positive man!!! Sapien!! :p """
    return [
        review for review in reviews
        if review[DERIVED_INSIGHTS][SENTIMENT]["compound"] < 0.0
    ]


def get_top_tweets_link(review_list):
    return [
        review[PROPERTIES][KEY_WITH_TWEET_URL]
        for review in review_list
        if review[CHANNEL_TYPE] == CHANNEL_TYPE_TWITTER
    ]


def calculate_hash(string):
    return hashlib.sha1(string.encode("utf-8")).hexdigest()


def most_common(L):
    # https://stackoverflow.com/a/1520716/3751615
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item

    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
            # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def get_sentiment_compound(review):
    return review[DERIVED_INSIGHTS][SENTIMENT][COMPOUND]


def filter_reviews(reviews, app_config, enable_key=IS_CHANNEL_ENABLED):
    print("[LOG] Filtering by :: ", enable_key)
    print("[LOG] REVIEW's before filtering :: ", len(reviews))

    channel_list = []
    # We create a list of channels which are enabled
    for review_config in app_config[REVIEW_CHANNELS]:
        if review_config[enable_key]:
            channel_list.append(review_config[CHANNEL_NAME])

    # We first filter the REVIEW on channel-type
    reviews = filter_review_on_channel(channel_list, reviews)

    print("[LOG] REVIEW's after filter on channel-type :: ", len(reviews))

    if ALGORITHM_DAYS_FILTER in app_config:
        # We now filter based on time
        current_date_time = datetime.now()
        from_date = current_date_time - \
            timedelta(days=app_config[ALGORITHM_DAYS_FILTER])
        reviews = filter_review_on_time(reviews, from_date)

    print("[LOG] REVIEW's after filter on time :: ", len(reviews))

    return reviews


def filter_review_for_slack(reviews, app_config):
    # We now filter based on time
    current_date_time = datetime.now()

    print("[LOG] Current Time is : ",
          current_date_time.strftime('%Y/%m/%d %H:%M:%S'))

    from_date = current_date_time - \
        timedelta(minutes=app_config[SLACKBOT_MINUTES_FILTER])
    reviews = filter_review_on_time(reviews, from_date)

    print("[LOG] REVIEW's after filter on slackbot time :: ", len(reviews))

    return reviews


def fetch_channel_config(app_config, channel_name):
    for channel_config in app_config[REVIEW_CHANNELS]:
        if channel_config[CHANNEL_NAME] == channel_name:
            return channel_config
    return None


def decrypt_config(app_config):
    """
    - Replaces the ENV variables with their values. These values are stored in local and circleCI env.
    - Returns app_config json with reaplced values
    """
    env_list = app_config[ENV_KEYS]
    app_config_formatted = json.dumps(app_config)

    for key in env_list:
        app_config_formatted = app_config_formatted.replace(
            key, os.environ[key])

    replaced_app_config = json.loads(app_config_formatted)
    return replaced_app_config


def validate_app_config(app_config):
    print("[LOG] Validating app-config schema")
    app_json_schema = open_json("src/app-config-schema.json")
    try:
        jsonschema.validate(app_config, app_json_schema)
    except jsonschema.exceptions.ValidationError as e:
        print("[Error] Parsing {file_name}. Error is {error}".format(
            file_name=APP_CONFIG_FILE.format(file_name=app), error=e))
        return False
    except json.decoder.JSONDecodeError as e:
        print(
            "[Error] Parsing the schema file itself! This can be catastrophic!")
        return False
    print("[LOG] Validating app-config schema successful")
    return True
