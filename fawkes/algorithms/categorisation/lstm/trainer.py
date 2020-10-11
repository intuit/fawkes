# The entire file is mostly a replication of the open-source implementation
# Source:
# https://github.com/susanli2016/PyCon-Canada-2019-NLP-Tutorial/blob/master/BBC%20News_LSTM.ipynb
import csv
import json
import re
import sys
import os
import tensorflow as tf
import numpy as np
import nltk
import pathlib

nltk.download("stopwords", quiet=True)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pprint import pprint
from nltk.corpus import stopwords

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants
from fawkes.configs.app_config import AppConfig, ReviewChannelTypes, CategorizationAlgorithms
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review

STOPWORDS = set(stopwords.words("english"))

# Our default configuration
VOCAB_SIZE = 5000
EMBEDDING_DIM = 64
MAX_LENGTH = 200
TRUNC_TYPE = "post"
PADDING_TYPE = "post"
OOV_TOK = "<OOV>"
TRAINING_PORTION = 0.8
NUM_EPOCHS = 10


def get_articles_and_labels(reviews, labels=[]):
    """
    Given a list of reviews returns a tuple of review, category
    We call them articles and labels
    Ideally if you want to implement the LSTM classifier for a different data-set, you should only have to change this function
    """
    articles = []

    # In this process we clean up the original labels
    # This is required because these labels will be tokenized afterwards
    # We need to maintain a mapping of what the original labels were
    cleaned_labels = {}

    # We go through the list of reviews
    for review in reviews:
        article = review.message
        label = review.derived_insight.category

        # Now we remove stopwords
        for word in STOPWORDS:
            token = " " + word + " "
            article = article.replace(token, " ")
            article = article.replace(" ", " ")

        # Remove leading and ending spaces
        article.strip()

        # We remove the empty/usless articles
        if article == "" or article == constants.NA_STRING:
            continue

        # Cleaning up the labels
        cleaned_label = re.sub(r"\W+", "", label)
        cleaned_labels[cleaned_label] = label

        articles.append(article)
        labels.append(cleaned_label)

    return (articles, labels, cleaned_labels)


def split_data(articles, labels):
    train_size = int(len(articles) * TRAINING_PORTION)

    train_articles = articles[0:train_size]
    train_labels = labels[0:train_size]

    validation_articles = articles[train_size:]
    validation_labels = labels[train_size:]

    return (train_articles, train_labels, validation_articles, validation_labels)


def train(articles, labels):
    print("[LOG] LSTM pre-processing started")
    # Splitting the data into training and validation set
    train_articles, train_labels, validation_articles, validation_labels = split_data(
        articles, labels
    )

    # Now we tokenize the articles and labels
    # We find the token for each word and store it.
    article_tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token=OOV_TOK)
    article_tokenizer.fit_on_texts(train_articles)

    # After we have the token for the top (5000) VOCAB_SIZE words
    # We convert the text to a list of tokens
    train_sequences = article_tokenizer.texts_to_sequences(train_articles)
    validation_sequences = article_tokenizer.texts_to_sequences(validation_articles)

    # We pad/truncate the sequences to appropriate length
    train_padded = pad_sequences(
        train_sequences, maxlen=MAX_LENGTH, padding=PADDING_TYPE, truncating=TRUNC_TYPE
    )
    validation_padded = pad_sequences(
        validation_sequences,
        maxlen=MAX_LENGTH,
        padding=PADDING_TYPE,
        truncating=TRUNC_TYPE,
    )

    # We do the same things on labels also
    label_tokenizer = Tokenizer()
    label_tokenizer.fit_on_texts(labels)

    training_label_seq = np.array(label_tokenizer.texts_to_sequences(train_labels))
    validation_label_seq = np.array(
        label_tokenizer.texts_to_sequences(validation_labels)
    )
    print("[LOG] LSTM pre-processing completed")

    print("[LOG] LSTM building model started")
    model = tf.keras.Sequential(
        [
            # Add an Embedding layer expecting input vocab of size 5000, and output
            # embedding dimension of size 64 we set at the top
            tf.keras.layers.Embedding(VOCAB_SIZE, EMBEDDING_DIM),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(EMBEDDING_DIM)),
            # use ReLU in place of tanh function since they are very good
            # alternatives of each other.
            tf.keras.layers.Dense(EMBEDDING_DIM, activation="relu"),
            # Add a Dense layer with 6 units and softmax activation.
            # When we have multiple outputs, softmax convert outputs layers into a
            # probability distribution.
            tf.keras.layers.Dense(len(set(labels)) + 1, activation="softmax"),
        ]
    )
    model.summary()
    model.compile(
        loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"]
    )
    print("[LOG] LSTM building model completed")

    print("[LOG] LSTM training model started")

    # Getting down to business
    model.fit(
        train_padded,
        training_label_seq,
        epochs=NUM_EPOCHS,
        validation_data=(validation_padded, validation_label_seq),
        verbose=2,
    )

    print("[LOG] LSTM training model completed")

    return model, article_tokenizer, label_tokenizer


def train_lstm_model(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
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
        print("[LOG] going through app config ", app_config.app.name)

        # Path where the user reviews were stored after parsing.
        processed_user_reviews_file_path = constants.PROCESSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.processed_data_folder,
            app_name=app_config.app.name,
        )

        if not (
            app_config.algorithm_config.categorization_algorithm != None
            and app_config.algorithm_config.categorization_algorithm == CategorizationAlgorithms.LSTM_CLASSIFICATION
        ):
            continue

       # Loading the reviews
        reviews = utils.open_json(processed_user_reviews_file_path)

        # Converting the json object to Review object
        reviews = [Review.from_review_json(review) for review in reviews]

        # reviews = utils.filter_reviews(reviews, app_config)

        articles, labels, cleaned_labels = get_articles_and_labels(
            reviews
        )

        trained_model, article_tokenizer, label_tokenizer = train(articles, labels)

        trained_lstm_categorization_model_file_path = constants.LSTM_CATEGORY_MODEL_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.models_folder,
            app_name=app_config.app.name,
        )

        dir_name = os.path.dirname(trained_lstm_categorization_model_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        trained_model.save(trained_lstm_categorization_model_file_path)

        # Saving the tokenizers
        utils.dump_json(
            article_tokenizer.to_json(),
            constants.LSTM_CATEGORY_ARTICLE_TOKENIZER_FILE_PATH.format(
                base_folder=app_config.fawkes_internal_config.data.base_folder,
                dir_name=app_config.fawkes_internal_config.data.models_folder,
                app_name=app_config.app.name,
            ),
        )

        # Saving the tokenizers
        utils.dump_json(
            label_tokenizer.to_json(),
            constants.LSTM_CATEGORY_LABEL_TOKENIZER_FILE_PATH.format(
                base_folder=app_config.fawkes_internal_config.data.base_folder,
                dir_name=app_config.fawkes_internal_config.data.models_folder,
                app_name=app_config.app.name,
            ),
        )
