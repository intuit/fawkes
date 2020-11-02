"""
    Module for calculating similarity of reviews against a query.
    Implemented using: https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
"""

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd
import sys
import pathlib
import logging

from datetime import datetime, timedelta, timezone

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants
import fawkes.utils.filter_utils as filter_utils
import fawkes.constants.logs as logs

from fawkes.review.review import Review
from fawkes.configs.app_config import AppConfig
from fawkes.cli.fawkes_actions import FawkesActions

module_url = constants.SENTENCE_ENCODER_MODEL
model = hub.load(module_url)

def embed_reviews(reviews):
    return model(reviews)

def get_similar_reviews(reviews, query, num_results):
    # We generate the emdedding of the query
    embedded_query = model([query])

    # Compute the similarity score for all the review w.r.t to this review
    similarity_scores = [
        np.inner(
            embedded_query[0], review.derived_insight.review_message_encoding
        )
        for review in reviews
    ]

    reviews_with_scores = list(zip(similarity_scores, reviews))
    reviews_with_scores = sorted(reviews_with_scores, reverse=True)

    return reviews_with_scores[:num_results]

def get_similar_reviews_for_app(app_config_file, query, num_results):
    # Creating an AppConfig object
    app_config = AppConfig(
        utils.open_json(
            app_config_file
        )
    )

    # Log the current operation which is being performed.
    logging.info(logs.QUERY_START, FawkesActions.QUERY_SIMILAR_REVIEWS, "ALL", app_config.app.name)

    # Path where the user reviews were stored after parsing.
    processed_user_reviews_file_path = constants.PROCESSED_USER_REVIEWS_FILE_PATH.format(
        base_folder=app_config.fawkes_internal_config.data.base_folder,
        dir_name=app_config.fawkes_internal_config.data.processed_data_folder,
        app_name=app_config.app.name,
    )

    # Loading the reviews
    reviews = utils.open_json(processed_user_reviews_file_path)

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

    similar_reviews =  get_similar_reviews(reviews, query, num_results)

    # Log the current operation which is being performed.
    logging.info(logs.QUERY_END, FawkesActions.QUERY_SIMILAR_REVIEWS, "ALL", app_config.app.name)

    # Create the intermediate folders
    query_results_file_path = constants.QUERY_RESULTS_FILE_PATH.format(
        base_folder=app_config.fawkes_internal_config.data.base_folder,
        dir_name=app_config.fawkes_internal_config.data.query_folder,
        app_name=app_config.app.name,
        query_hash=utils.calculate_hash(query)
    )

    dir_name = os.path.dirname(query_results_file_path)
    pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

    utils.dump_json(
        [
            {
                "score": score,
                "review": review.to_dict(),
            }
            for score, review in similar_reviews
        ],
        query_results_file_path,
    )


