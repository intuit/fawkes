import re
import sys
import os
import json

from nltk.stem.wordnet import WordNetLemmatizer

sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants as constants

from fawkes.app_config.app_config import AppConfig

lmtzr = WordNetLemmatizer()

def parse_keywords_file(keyword_file_name, enable_remove_stop_words=True):
    # Topics is a dict, key = Topic Name. value = list of words and weights.
    topics = {}
    keywords_list = utils.open_json(keyword_file_name)
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
            cleaned_line = utils.remove_stop_words(cleaned_line)
        # For each word assign a weight
        for word in list(set(cleaned_line)):
            # Add the word to the topic
            topic[lmtzr.lemmatize(word.lower())] = 1
        topics[topic_keyword] = topic
    return topics

def generate_keyword_weights():
    app_configs = utils.open_json(
         constants.APP_CONFIG_FILE.format(file_name=constants.APP_CONFIG_FILE_NAME)
    )
    for app_config_file in app_configs:
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
        # First look at the category keywords.
        utils.dump_json(
            parse_keywords_file(
                app_config.algorithm_config.category_keywords_file
            ),
            app_config.algorithm_config.category_keywords_weights_file,
        )
        # Then look at the bug-feature keywords
        utils.dump_json(
            parse_keywords_file(
                app_config.algorithm_config.bug_feature_keywords_file,
                False
            ),
            app_config.algorithm_config.bug_feature_keywords_weights_file,
        )

if __name__ == "__main__":
    generate_keyword_weights()
