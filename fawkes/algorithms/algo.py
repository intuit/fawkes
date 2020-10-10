import sys
import os
import importlib
import tensorflow as tf
import pathlib
import re

from pprint import pprint
from multiprocessing import Pool
from functools import partial
from datetime import datetime, timedelta, timezone

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.utils.filter_utils as filter_utils
import fawkes.constants.constants as constants
import fawkes.algorithms.categorisation.lstm.categoriser as lstm_categoriser
import fawkes.algorithms.categorisation.text_match.categoriser as text_match_categoriser

from fawkes.configs.app_config import AppConfig, ReviewChannelTypes, CategorizationAlgorithms
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review
from fawkes.algorithms.sentiment.sentiment import get_sentiment

def add_review_sentiment_score(review):
    # Add the sentiment to the review's derived insight and return the review
    review.derived_insight.sentiment = get_sentiment(review.message)
    # Return the review
    return review

def text_match_categortization(review, app_config, topics):
    # Find the category of the review
    category_scores, category = text_match_categoriser.text_match(review.message, topics)
    # Add the category to the review's derived insight and return the review
    review.derived_insight.category = category
    # Add the category scores.
    review.derived_insight.extra_properties[constants.CATEGORY_SCORES] = category_scores
    # Return the review
    return review


def lstm_classification(reviews, model, article_tokenizer, label_tokenizer, cleaned_labels):
    articles = [review.message for review in reviews]
    # Get the categories for each of the reviews
    categories = lstm_categoriser.predict_labels(
        articles,
        model,
        article_tokenizer,
        label_tokenizer
    )

    for index, review in enumerate(reviews):
        review.derived_insight.extra_properties[constants.LSTM_CATEGORY] = cleaned_labels[categories[index]]

    return reviews


def bug_feature_classification(review, topics):
    _, category = text_match_categoriser.text_match(review.message, topics)
    # Add the bug-feature classification to the review's derived insight and return the review
    review.derived_insight.extra_properties[constants.BUG_FEATURE] = category
    # Return the review
    return review

def run_algo(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
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
        # Path where the user reviews were stored after parsing.
        parsed_user_reviews_file_path = constants.PARSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.parsed_data_folder,
            app_name=app_config.app.name,
        )

        # Loading the reviews
        reviews = utils.open_json(parsed_user_reviews_file_path)

        # Converting the json object to Review object
        reviews = [Review.from_review_json(review) for review in reviews]

        # Filtering out reviews which are not applicable.
        reviews = filter_utils.filter_reviews_by_time(
            filter_utils.filter_reviews_by_channel(
                reviews, filter_utils.filter_disabled_review_channels(
                    app_config
                ),
            ),
            datetime.now(timezone.utc) - timedelta(days=app_config.algorithm_config.algorithm_days_filter)
        )

        # Number of process to make
        num_processes = min(constants.PROCESS_NUMBER, os.cpu_count())

        if constants.CIRCLECI in os.environ:
            num_processes = 2

        # Adding sentiment
        with Pool(num_processes) as process:
            reviews = process.map(add_review_sentiment_score, reviews)

        if app_config.algorithm_config.categorization_algorithm != None and app_config.algorithm_config.category_keywords_weights_file != None:
            # We read from the topic file first
            topics = {}
            topics = utils.open_json(app_config.algorithm_config.category_keywords_weights_file)

            # Adding text-match categorization
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(
                        text_match_categortization,
                        app_config=app_config,
                        topics=topics
                    ),
                    reviews
                )

        if app_config.algorithm_config.bug_feature_keywords_weights_file != None:
            # We read from the topic file first
            topics = {}
            topics = utils.open_json(app_config.algorithm_config.bug_feature_keywords_weights_file)

            # Adding bug/feature classification
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(
                        bug_feature_classification,
                        topics=topics
                    ),
                    reviews
                )

        if app_config.algorithm_config.categorization_algorithm == CategorizationAlgorithms.LSTM_CLASSIFICATION:
            # Load the TensorFlow model
            model = tf.keras.models.load_model(
                constants.LSTM_CATEGORY_MODEL_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.models_folder,
                    app_name=app_config.app.name,
                )
            )

            # Load the article tokenizer file
            tokenizer_json = utils.open_json(
               constants.LSTM_CATEGORY_ARTICLE_TOKENIZER_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.models_folder,
                    app_name=app_config.app.name,
                ),
            )
            article_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                tokenizer_json
            )

            # Load the label tokenizer file
            tokenizer_json = utils.open_json(
                constants.LSTM_CATEGORY_LABEL_TOKENIZER_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.models_folder,
                    app_name=app_config.app.name,
                ),
            )
            label_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                tokenizer_json
            )

            cleaned_labels = {}
            for review in reviews:
                label = review.derived_insight.category
                cleaned_label = re.sub(r'\W+', '', label)
                cleaned_label = cleaned_label.lower()
                cleaned_labels[cleaned_label] = label

            # Adding LSTM categorization
            reviews = lstm_classification(
                reviews,
                model,
                article_tokenizer,
                label_tokenizer,
                cleaned_labels
            )

        # Create the intermediate folders
        processed_user_reviews_file_path = constants.PROCESSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.processed_data_folder,
            app_name=app_config.app.name,
        )

        dir_name = os.path.dirname(processed_user_reviews_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        utils.dump_json(
            [review.to_dict() for review in reviews],
            processed_user_reviews_file_path,
        )
