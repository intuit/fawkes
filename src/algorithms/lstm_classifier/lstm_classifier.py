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

nltk.download("stopwords")

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pprint import pprint
from nltk.corpus import stopwords

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import src.utils as utils
from src.config import *
from src.utils import *

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
    Given a list of reviews (in unified json format) returns a tuple of review, category
    We call them articles and labels
    Ideally if you want to implement the LSTM classifier for a different data-set, you should only have to change this function
    """
    articles = []

    # In this process we clean up the original labels
    # This is required because these labels will be tokenized afterwards
    # We need to maintain a mapping of what the original labels were
    original_label_to_clean_label = {}

    # We go through the list of reviews
    for review in reviews:
        article = review[MESSAGE]
        label = review[DERIVED_INSIGHTS][CATEGORY]

        # Now we remove stopwords
        for word in STOPWORDS:
            token = " " + word + " "
            article = article.replace(token, " ")
            article = article.replace(" ", " ")

        # Remove leading and ending spaces
        article.strip()

        # We remove the empty/usless articles
        if article == "" or article == NA_STRING:
            continue

        # Cleaning up the labels
        cleaned_label = re.sub(r"\W+", "", label)
        original_label_to_clean_label[cleaned_label] = label

        articles.append(article)
        labels.append(cleaned_label)

    return (articles, labels, original_label_to_clean_label)


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


def train_lstm_model():
    app_configs = open_json(APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    # We process all algorithms on parsed data for each app
    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not utils.validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)

        if not (
            CATEGORIZATION_ALGORITHM in app_config
            and app_config[CATEGORIZATION_ALGORITHM] == LSTM_CLASSIFIER
        ):
            continue

        # Loading the REVIEW's
        reviews = utils.open_json(
            PROCESSED_INTEGRATED_REVIEW_FILE.format(app_name=app_config[APP])
        )

        # reviews = utils.filter_reviews(reviews, app_config)

        articles, labels, original_label_to_clean_label = get_articles_and_labels(
            reviews
        )

        trained_model, article_tokenizer, label_tokenizer = train(articles, labels)

        if not os.path.exists(TRAINED_MODELS):
            os.makedirs(TRAINED_MODELS)

        trained_model.save(LSTM_TRAINED_MODEL_FILE.format(app_name=app_config[APP]))

        # Saving the tokenizers
        dump_json(
            article_tokenizer.to_json(),
            LSTM_ARTICLE_TOKENIZER_FILE.format(app_name=app_config[APP]),
        )

        # Saving the tokenizers
        dump_json(
            label_tokenizer.to_json(),
            LSTM_LABEL_TOKENIZER_FILE.format(app_name=app_config[APP]),
        )


def predict_labels(articles, app_config, model, article_tokenizer, label_tokenizer):
    """ Given an article we predict the label """

    # Convert the give article to tokens
    tokenized_articles = article_tokenizer.texts_to_sequences(articles)
    # Add padding
    tokenized_articles = pad_sequences(
        tokenized_articles,
        maxlen=MAX_LENGTH,
        padding=PADDING_TYPE,
        truncating=TRUNC_TYPE,
    )

    # Predict the label
    predictions = model.predict(tokenized_articles)

    # Now to find out the label, we have to do a reverse index search on the
    # label_tokens
    label_names = dict(
        (token, label_name)
        for (label_name, token) in label_tokenizer.word_index.items()
    )

    labels = [label_names[np.argmax(prediction)] for prediction in predictions]

    return labels


if __name__ == "__main__":
    train_lstm_model()
