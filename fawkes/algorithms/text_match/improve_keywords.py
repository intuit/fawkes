import sys
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from pprint import pprint

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

from fawkes.config import *
from fawkes.utils import *


def tfidf_generator(corpus,
                    corpus_category_list,
                    keywords_number,
                    bigram=False):
    """
    Takes corpus as input which is list of sentences in different topics.
    Output : [{"account": 0.2,"ad": 0.1,},{"account": 0.3,"case": 0.1}]
    """
    keywords_dict = {}
    documents_with_weight = {}

    # initialize
    if bigram:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    else:
        vectorizer = TfidfVectorizer()
    # This generates the tf-idf scores for every document-term
    tf_idf_matrix = vectorizer.fit_transform(corpus).toarray()
    # Gives the vocabulary learnt from corpus ["word1", "word2", ...."wordn"]
    keywords_vocab = vectorizer.get_feature_names()

    # topic_dict :- {word1:tf-idfscore, word2:score}
    for topic_index in range(len(tf_idf_matrix)):
        topic_dict = {}
        for word_index in range(len(tf_idf_matrix[topic_index])):
            topic_dict[keywords_vocab[word_index]] = tf_idf_matrix[topic_index][
                word_index]
        # Sorting based on weights
        topic_dict = {
            word: topic_dict[word] for word in sorted(
                topic_dict, key=topic_dict.get, reverse=True)[:keywords_number]
        }
        documents_with_weight[corpus_category_list[topic_index]] = topic_dict

    return documents_with_weight


def create_category_dict(keywords_list):
    """
    Creating dictionary of topics and initializing with values as empty list.
    Had to find an efficient way of concatenating all reviews belonging to one category
    """
    reviews_per_category = {}

    for topic in keywords_list:
        reviews_per_category[topic] = []

    return reviews_per_category


def create_corpus(reviews, category_dict):
    """Returns a list of sentences in each category.Concatenates all the reviews belonging to one category and put in a list"""
    # list of reviews in each category
    corpus = []
    corpus_category = []

    # Category_dict format {topic1: [reviews in topic1],"topic2": [reviews in
    # topic2]}
    for review in reviews:
        if review.derived_insight.category != "uncategorized":
            # If list is empty
            if not category_dict[review.derived_insight.category]:
                category_dict[review.derived_insight.category] = " ".join(
                    remove_stop_words(tokenise(review.message)))
            else:
                category_dict[review.derived_insight.category] += " ".join(
                    remove_stop_words(tokenise(review.message)))

    # Our corpus - ["reviews in topic1","reviews in tpoic2"]
    for topic in category_dict:
        # To reomove those topics which have empty list of reviews
        if category_dict[topic]:
            corpus.append(category_dict[topic])
            corpus_category.append(topic)

    return (corpus, corpus_category)


def improve_categorywise_keywords(reviews, keywords_list):
    """ Takes unified json as input. preprocesses for tf-idf calculation """

    top_keywords_in_categories = {}

    # We create a dictionary with topic as key and value as an empty list
    # {topic1 : [], topic2: []}
    reviews_per_category_dict = create_category_dict(keywords_list)

    # We now append reviews belonging to one category together in the dictionary we just created. corpus required format is created then
    # corpus- [d1, d2] , corpus_category_list- [topic1, topic2]
    # This is to maintain good friendship with reviews and their topics. They
    # shouldn't get lost. :) :(
    corpus, corpus_category_list = create_corpus(reviews,
                                                 reviews_per_category_dict)

    # [{"account": 0.2,"ad": 0.1,},{"account": 0.3,"case": 0.1}]
    documents_with_weight = tfidf_generator(corpus, corpus_category_list,
                                            IMPROVEMENT_KEYWORDS_NUMBER)

    return documents_with_weight


if __name__ == "__main__":
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        if validate_app_config(app_config):
            app_config = decrypt_config(app_config)
            keywords_list = open_json(app_config[TOPIC_KEYWORDS_FILE])
            reviews = open_json(
                PROCESSED_INTEGRATED_REVIEW_FILE.format(
                    app_name=app_config.app.name))
            top_keywords_in_categories = improve_categorywise_keywords(
                reviews, keywords_list)
            dump_json(
                top_keywords_in_categories,
                IMPROVED_CATEGORY_KEYWORDS.format(app_name=app_config.app.name))
