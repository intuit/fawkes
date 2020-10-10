import sys
import os
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

from fawkes.algorithms.categorisation.lstm.trainer import MAX_LENGTH, PADDING_TYPE, TRUNC_TYPE

def predict_labels(articles, model, article_tokenizer, label_tokenizer):
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
