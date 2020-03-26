import re
import sys
import os
import json

from nltk.stem.wordnet import WordNetLemmatizer

sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *

lmtzr = WordNetLemmatizer()


def parse_keywords_file(keyword_file_name, enable_remove_stop_words=True):
    # Topics is a dict, key = Topic Name. value = list of words and weights.
    topics = {}
    keywords_list = open_json(keyword_file_name)
    for topic_keyword in keywords_list:
        topic = {}
        line = " ".join(keywords_list[topic_keyword])

        # Remove all trailing and beginning write spaces
        line = line.lower()
        line = line.strip()
        # We will replace all the non-alphabet charectors with a space
        cleaned_line = re.sub("[^a-zA-Z]+", " ", line)
        # Replace multiple spaces with a single space
        cleaned_line = re.sub(" +", " ", cleaned_line)
        # Split the line according to space to get the words
        cleaned_line = cleaned_line.split()
        # Remove the stopwords.
        if enable_remove_stop_words:
            cleaned_line = remove_stop_words(cleaned_line)
        # For each word assign a weight
        for word in list(set(cleaned_line)):
            # Add the word to the topic
            topic[lmtzr.lemmatize(word.lower())] = 1
        topics[topic_keyword] = topic
    return topics


if __name__ == "__main__":
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        if validate_app_config(app_config):
            app_config = decrypt_config(app_config)
            dump_json(parse_keywords_file(app_config[TOPIC_KEYWORDS_FILE]),
                      TOPICS_WEIGHT_FILE.format(app=app_config[APP]))
            dump_json(parse_keywords_file(app_config[BUG_FEATURE_FILE], False),
                      BUG_FEATURE_FILE_WITH_WEIGHTS.format(app=app_config[APP]))
