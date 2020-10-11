import re
import sys
import os
import json
import nltk

from pprint import pprint
from nltk.stem.wordnet import WordNetLemmatizer

sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

lmtzr = WordNetLemmatizer()
nltk.download("wordnet", quiet=True)

def isBigram(word):
    if " " in word:
        return True
    else:
        return False


def getBigramsFromTopic(topic):
    bigrams = []
    for word in topic:
        if isBigram(word):
            bigrams.append(word)
    return bigrams


def text_match(text, list_of_topics):
    """
    Matches the given string with a list of topics and give the topic which has the best match.
    - Currently we are doing a plain text match.
    @param text: The text to be matched with topics
    @param topics: A list of list containing keywords related to each topic.
    """

    words = text.split()
    scores = {}

    # For a particular text, we go thorugh all the topics.
    for topic in list_of_topics:
        # For each topic we create a score of how much the text matches the
        # words in the topic
        scores[topic] = 0

        # First we will get all the bigrams of the topic
        bigrams = getBigramsFromTopic(list_of_topics[topic])

        # Add weight of each bi-gram separately
        for bigram in bigrams:
            if bigram in text:
                scores[topic] += list_of_topics[topic][bigram]

        # Go through all the words in a topic
        for word in words:
            try:
                word = re.sub(r"\W+", "", word)
                lem_word = lmtzr.lemmatize(word.lower())
                if lem_word in list_of_topics[topic]:
                    # For each matching work, add the weight.
                    # Currently we are just adding the weight, but we need to give less priority to repeated words.
                    # What might be a good way to do that ?
                    # Law of diminishing returns ?
                    scores[topic] += list_of_topics[topic][lem_word]
            except BaseException:
                print(
                    "[ERROR] Error In text_match! You should check this. This can be FATAL."
                )
                pass
    category = max(scores, key=lambda key: scores[key])

    # If the score is not found, let make it uncategorized
    if max(scores.values()) == 0:
        category = constants.CATEGORY_NOT_FOUND

    return scores, category
