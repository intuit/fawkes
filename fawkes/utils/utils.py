import json
import sys
import os
import re
import csv
import itertools
import operator
import dateutil.parser
import hashlib

import spacy
import jsonschema

from pprint import pprint
from datetime import datetime, timedelta

from nltk.corpus import stopwords
from pathlib import Path

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.constants.constants as constants
from fawkes.constants.stop_words import EXTENDED_STOP_WORDS

def open_json(file_location):
    with open(file_location, "r") as read_file:
        documents = json.load(read_file)
    return documents


def dump_json(records, write_file):
    with open(write_file, "w") as file:
        json.dump(records, file, indent=4)

def dump_csv(records, write_file):
    #Get the column values from query response
    field_names = list(records.keys())
    #Write the value corresponding to above columns in csv file
    with open(write_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerow(records)

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

def check_tweet_authenticity(tweet_message, twitter_handle_blacklist):
    """  Checks if tweets incoming are authentic. basically there is blacklist of twitter-handles """
    is_tweet_authentic = True

    for handle in twitter_handle_blacklist:
        if handle in tweet_message:
            is_tweet_authentic = False

    return is_tweet_authentic


def check_for_explicit_content(tweet):
    if constants.POSSIBLY_SENSITIVE in tweet:
        return tweet[constants.POSSIBLY_SENSITIVE]
    return True

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
    return review.derived_insight.sentiment["compound"]


def fetch_channel_config(app_config, channel_type):
    for review_channel in app_config.review_channels:
        if review_channel.channel_type == channel_type:
            return review_channel
    return None

def write_query_results(response, write_file, format):
    # Create the intermediate folders
    dir_name = os.path.dirname(write_file)
    Path(dir_name).mkdir(parents=True, exist_ok=True)
    if format == constants.JSON:
        dump_json(response, write_file)
    elif format == constants.CSV:
        dump_csv(response, write_file)
