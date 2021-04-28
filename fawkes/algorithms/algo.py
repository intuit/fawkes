import numpy as np
from fawkes.cli.fawkes_actions import FawkesActions
from fawkes.review.review import Review
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.configs.app_config import AppConfig, ReviewChannelTypes, CategorizationAlgorithms, Algorithms
import fawkes.constants.logs as logs
import fawkes.constants.constants as constants
import fawkes.utils.filter_utils as filter_utils
import fawkes.utils.utils as utils
import sys
import os
import importlib
import pathlib
import re
import logging

from pprint import pprint
from multiprocessing import Pool
from functools import partial
from datetime import datetime, timedelta, timezone

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))


def add_review_sentiment_score(review):
    # WE import the module only when its required.
    from fawkes.algorithms.sentiment.sentiment import get_sentiment

    # Add the sentiment to the review's derived insight and return the review
    review.derived_insight.sentiment = get_sentiment(review.message)
    # Return the review
    return review


def add_review_message_encoding(review, encoding):
    # Add the review message's encoding as a derived insight.
    # We first convert the tensor object to a numpy array and then to a list
    # so that it can be saved as a json.
    review.derived_insight.review_message_encoding = encoding.numpy().tolist()
    # Return the review
    return review


def text_match_categortization(review, app_config, topics):
    # WE import the module only when its required.
    import fawkes.algorithms.categorisation.text_match.categoriser as text_match_categoriser

    # Find the category of the review
    category_scores, category = text_match_categoriser.text_match(
        review.message, topics)
    # Add the category to the review's derived insight and return the review
    review.derived_insight.category = category
    # Add the category scores.
    review.derived_insight.extra_properties[constants.CATEGORY_SCORES] = category_scores
    # Return the review
    return review


def bug_feature_classification(review, topics):
    # WE import the module only when its required.
    import fawkes.algorithms.categorisation.text_match.categoriser as text_match_categoriser

    _, category = text_match_categoriser.text_match(review.message, topics)
    # Add the bug-feature classification to the review's derived insight and
    # return the review
    review.derived_insight.extra_properties[constants.BUG_FEATURE] = category
    # Return the review
    return review


def lstm_classification(
        reviews,
        model,
        article_tokenizer,
        label_tokenizer,
        cleaned_labels):
    # WE import the module only when its required.
    import fawkes.algorithms.categorisation.lstm.categoriser as lstm_categoriser

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


def run_sentiment_analysis(reviews, app_config, num_processes):
    if Algorithms.SENTIMENT_ANALYSIS in app_config.algorithm_config.algorithms_to_run:
        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_START,
            'SENTIMENT_ANALYSIS',
            "ALL",
            app_config.app.name)

        # Adding sentiment
        with Pool(num_processes) as process:
            reviews = process.map(add_review_sentiment_score, reviews)

        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_END,
            'SENTIMENT_ANALYSIS',
            "ALL",
            app_config.app.name)

    return reviews


def run_categorization(reviews, app_config, num_processes):
    if Algorithms.CATEGORIZATION in app_config.algorithm_config.algorithms_to_run:
        if app_config.algorithm_config.categorization.algorithm == CategorizationAlgorithms.TEXT_MATCH_CLASSIFICATION:
            # Log the number of reviews we got.
            logging.info(
                logs.CURRENT_ALGORITHM_START,
                CategorizationAlgorithms.TEXT_MATCH_CLASSIFICATION,
                "ALL",
                app_config.app.name)

            # We read from the topic file first
            topics = {}
            topics = utils.open_json(
                app_config.algorithm_config.categorization.category_keywords_weights_file)

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

            # Log the number of reviews we got.
            logging.info(
                logs.CURRENT_ALGORITHM_END,
                CategorizationAlgorithms.TEXT_MATCH_CLASSIFICATION,
                "ALL",
                app_config.app.name)
        elif app_config.algorithm_config.categorization.algorithm == CategorizationAlgorithms.LSTM_CLASSIFICATION:
            # WE import the module only when its required.
            import tensorflow as tf

            # Log the number of reviews we got.
            logging.info(
                logs.CURRENT_ALGORITHM_START,
                CategorizationAlgorithms.LSTM_CLASSIFICATION,
                "ALL",
                app_config.app.name)

            # Load the TensorFlow model
            model = tf.keras.models.load_model(
                constants.LSTM_CATEGORY_MODEL_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.models_folder,
                    app_name=app_config.app.name,
                ))

            # Load the article tokenizer file
            tokenizer_json = utils.open_json(
                constants.LSTM_CATEGORY_ARTICLE_TOKENIZER_FILE_PATH.format(
                    base_folder=app_config.fawkes_internal_config.data.base_folder,
                    dir_name=app_config.fawkes_internal_config.data.models_folder,
                    app_name=app_config.app.name,
                ),
            )
            article_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                tokenizer_json)

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

            # Log the number of reviews we got.
            logging.info(
                logs.CURRENT_ALGORITHM_END,
                CategorizationAlgorithms.LSTM_CLASSIFICATION,
                "ALL",
                app_config.app.name)

        # Log the number of reviews we got.
        logging.info(
            logs.NUM_REVIEWS,
            len(reviews),
            "ALL",
            app_config.app.name)

    return reviews


def run_bug_feature_categorization(reviews, app_config, num_processes):
    if Algorithms.BUG_FEATURE_CATEGORIZATION in app_config.algorithm_config.algorithms_to_run:
        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_START,
            Algorithms.BUG_FEATURE_CATEGORIZATION,
            "ALL",
            app_config.app.name)

        # We read from the topic file first
        topics = {}
        topics = utils.open_json(
            app_config.algorithm_config.categorization.bug_feature_keywords_weights_file)

        # Adding bug/feature classification
        with Pool(num_processes) as process:
            reviews = process.map(
                partial(
                    bug_feature_classification,
                    topics=topics
                ),
                reviews
            )
        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_END,
            Algorithms.BUG_FEATURE_CATEGORIZATION,
            "ALL",
            app_config.app.name)

    return reviews


def run_review_text_encoding(reviews, app_config, num_processes):
    if Algorithms.MESSAGE_ENCODING in app_config.algorithm_config.algorithms_to_run:
        # WE import the module only when its required.
        from fawkes.algorithms.similarity.similarity import embed_reviews

        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_START,
            Algorithms.MESSAGE_ENCODING,
            "ALL",
            app_config.app.name)
        # Adding review text embeddings
        review_message_embeddings = embed_reviews([
            review.message for review in reviews
        ])
        reviews = [
            add_review_message_encoding(
                review, review_encoding) for review, review_encoding in list(
                zip(
                    reviews, review_message_embeddings))]
        # Log the number of reviews we got.
        logging.info(
            logs.CURRENT_ALGORITHM_END,
            Algorithms.MESSAGE_ENCODING,
            "ALL",
            app_config.app.name)

    return reviews


def run_algo(fawkes_config_file=constants.FAWKES_CONFIG_FILE):
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
        # Log the current operation which is being performed.
        logging.info(
            logs.OPERATION,
            FawkesActions.RUN_ALGO,
            "ALL",
            app_config.app.name)

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
                reviews,
                filter_utils.filter_disabled_review_channels(app_config),
            ),
            datetime.now(
                timezone.utc) -
            timedelta(
                days=app_config.algorithm_config.algorithm_days_filter))

        # Log the number of reviews we got.
        logging.info(
            logs.NUM_REVIEWS,
            len(reviews),
            "ALL",
            app_config.app.name)

        # Number of process to make
        num_processes = min(constants.PROCESS_NUMBER, os.cpu_count())

        if constants.CIRCLECI in os.environ:
            num_processes = 2

        # Running sentiment analysis
        reviews = run_sentiment_analysis(reviews, app_config, num_processes)

        # Running categorization
        reviews = run_categorization(reviews, app_config, num_processes)

        # Running bug/feature categorizatio
        reviews = run_bug_feature_categorization(
            reviews, app_config, num_processes)

        # Running the message encoding
        reviews = run_review_text_encoding(reviews, app_config, num_processes)

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
