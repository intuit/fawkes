import sys
import os
import importlib
import tensorflow as tf

from pprint import pprint
from multiprocessing import Pool
from functools import partial
from datetime import datetime, timedelta

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import src.algorithms.lstm_classifier.lstm_classifier as lstm_classifier
import src.utils as utils

from src.algorithms.text_match.text_match import *
from src.algorithms.slackbot import *
from src.algorithms.sentiment import *
from src.config import *


def add_review_sentiment_score(review):
    return format_output_json(review, None, get_sentiment(review[MESSAGE]))


def text_match_categortization(review, app_config, topics):
    category_scores, category = text_match(review[MESSAGE], topics)
    return format_output_json(review, category, None,
                              {"category-scores": category_scores})


def lstm_classification(reviews, app_config, model, article_tokenizer,
                        label_tokenizer, original_label_to_clean_label):
    articles = [review[MESSAGE] for review in reviews]
    categories = lstm_classifier.predict_labels(articles, app_config, model,
                                                article_tokenizer,
                                                label_tokenizer)

    return [
        format_output_json(
            review, None, None,
            {LSTM_CATEGORY: original_label_to_clean_label[categories[index]]})
        for index, review in enumerate(reviews)
    ]


def bug_feature_classification(review, app_config, topics):
    _, category = text_match(review[MESSAGE], topics)
    return format_output_json(review, None, None, {BUG_FEATURE: category})


def run_algo():
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    # We process all algorithms on parsed data for each app
    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not utils.validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)
        # Loading the REVIEW's
        reviews = utils.open_json(
            PARSED_INTEGRATED_REVIEW_FILE.format(app_name=app_config[APP]))

        reviews = utils.filter_reviews(reviews, app_config)

        # Number of process to make
        num_processes = min(PROCESS_NUMBER, os.cpu_count())

        if CIRCLECI in os.environ:
            num_processes = 2

        print("[LOG] :: ", app)
        print("[LOG] Parallelism :: ", num_processes)

        print("[LOG] Starting Sentiment Analysis :: ")

        # Adding sentiment
        with Pool(num_processes) as process:
            reviews = process.map(add_review_sentiment_score, reviews)

        print("[LOG] Ending Sentiment Analysis :: ")

        if TOPIC_KEYWORDS_FILE in app_config:

            print("[LOG] Starting Categorization :: ")

            # We read from the topic file first
            topics = {}
            topics = open_json(TOPICS_WEIGHT_FILE.format(app=app_config[APP]))

            # Adding text-match categorization
            # Multiprocessing for speeeeeeding up. Need For Speed!!!
            # Partial is for multiple argument functions
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(text_match_categortization,
                            app_config=app_config,
                            topics=topics), reviews)

            print("[LOG] Ending Categorization :: ")

        if CATEGORIZATION_ALGORITHM in app_config and app_config[
                CATEGORIZATION_ALGORITHM] == LSTM_CLASSIFIER:
            print("[LOG] Loading LSTM Model :: ")

            model = tf.keras.models.load_model(
                LSTM_TRAINED_MODEL_FILE.format(app_name=app_config[APP]))

            print("[LOG] Start Load of Token Files :: ")

            tokenizer_json = open_json(
                LSTM_ARTICLE_TOKENIZER_FILE.format(app_name=app_config[APP]))
            article_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                tokenizer_json)

            tokenizer_json = open_json(
                LSTM_LABEL_TOKENIZER_FILE.format(app_name=app_config[APP]))
            label_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                tokenizer_json)

            print("[LOG] End Load of Token Files :: ")

            print("[LOG] Starting LSTM Categorization :: ")

            original_label_to_clean_label = {}
            for review in reviews:
                label = review[DERIVED_INSIGHTS][CATEGORY]
                cleaned_label = re.sub(r'\W+', '', label)
                cleaned_label = cleaned_label.lower()
                # Convert this to lower case as the tokenized label is lower
                # case
                original_label_to_clean_label[cleaned_label] = label

            # Adding LSTM categorization
            reviews = lstm_classification(reviews, app_config, model,
                                          article_tokenizer, label_tokenizer,
                                          original_label_to_clean_label)

            lstm_text_match_parity = 0

            for review in reviews:
                if review[DERIVED_INSIGHTS][CATEGORY] != review[
                        DERIVED_INSIGHTS][EXTRA_PROPERTIES][LSTM_CATEGORY]:
                    lstm_text_match_parity += 1

            print("[LOG] Number of reviews classified differently : ",
                  lstm_text_match_parity)
            print("[LOG] Total Reviews : ", len(reviews))

            if len(reviews) != 0:
                print("[LOG] % inaccuracy : ",
                      (100.0 * lstm_text_match_parity) / len(reviews))

            print("[LOG] Ending LSTM Categorization :: ")

        if BUG_FEATURE_FILE in app_config:
            print("[LOG] Starting Bug/Feature Categorization :: ")

            topics = {}
            topics = open_json(
                BUG_FEATURE_FILE_WITH_WEIGHTS.format(app=app_config[APP]))
            # Adding bug/feature
            # Multiprocessing for speeeeeeding up. Need For Speed!!!
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(bug_feature_classification,
                            app_config=app_config,
                            topics=topics), reviews)

            print("[LOG] Ending Bug/Feature Categorization :: ")

        dump_json(
            reviews,
            PROCESSED_INTEGRATED_REVIEW_FILE.format(app_name=app_config[APP]))


if __name__ == "__main__":
    run_algo()
