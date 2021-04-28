import nltk
import nltk.data
import json
import fawkes.constants.constants as constants
from fawkes.configs.fawkes_config import FawkesConfig
import fawkes.utils.utils as utils
from fawkes.configs.app_config import (
    AppConfig,
    ReviewChannelTypes,
    CategorizationAlgorithms,
)
from fawkes.review.review import Review
import fawkes.email_summary.queries as queries
from nltk.tokenize import sent_tokenize
import os
import sys
import pathlib
from sklearn.cluster import KMeans
from gensim.summarization.summarizer import summarize
from sentence_transformers import SentenceTransformer
import logging
import fawkes.constants.logs as logs


def k_means_classification(sentences, num_clusters):
    """
        @param{list<string>}: sentences - List of review sentence
        @param{Integer}: num_clusters - User defined number of clusters
        @returns{list<list<string>}: clustered_sentences - List of clusters of sentences

        Groups similar sentences into clusters
    """
    # Reference : https://github.com/UKPLab/sentence-transformers

    # Loading pre-trained model - 'distilbert-base-nli-stsb-mean-tokens'
    embedder = SentenceTransformer("distilbert-base-nli-stsb-mean-tokens")
    corpus_embeddings = embedder.encode(sentences)

    # Apply k-means to groups similar sentences into 'num_clusters' clusters
    clustering_model = KMeans(n_clusters=num_clusters)
    clustering_model.fit(corpus_embeddings)
    # assign label to each sentence
    cluster_assignment = clustering_model.labels_

    # group similar labeled sentences
    clustered_sentences = {new_list: [] for new_list in range(num_clusters)}
    for i in range(len(cluster_assignment)):
        temp_list = clustered_sentences[cluster_assignment[i]]
        temp_list.append(sentences[i])
        clustered_sentences[cluster_assignment[i]] = temp_list

    return clustered_sentences


def summarize_text(text, word_count):
    """
        @param{string}: text - text corpus to summarize
        @param{integer}: word_count - max number of words in a summary
        @returns{list<string>}: generated summary

        function to summarize a piece of text
    """
    gen_summary = summarize(text, word_count=word_count).split("\n")
    # remove all empty reviews from the list
    gen_summary = [i for i in gen_summary if i]
    return gen_summary


def preprocess_review(reviews):
    """
        @param{list<Review>}: reviews - List of reviews class object
        @returns{list<string>}: processed_sentences - List of processed reviews

        Code to preprocess the data
            - extract messages from review object
            - tokenize
            - remove sentences of inappropriate lengths
    """
    processed_sentences = []

    for review in reviews:
        # Extract a message from review object
        review_message = review.message

        # Tokenize a message
        sentences = sent_tokenize(review_message)

        # reject sentences of inappropriate lengths
        for sentence in sentences:
            word_count = len(sentence.split())
            if (
                word_count > constants.min_words_in_sentence
                and word_count < constants.max_words_in_sentence
            ):
                processed_sentences.append(sentence)
    return processed_sentences


def generate_summary(fawkes_config_file=constants.FAWKES_CONFIG_FILE):
    """
        @param{string}: fawkes_config_file - config file path
        @returns{map<string,list<string>>}: summarized_reviews - summarized reviews per category

        Main function to create a summary of reviews
            - queries to get reviews
            - preprocess reviews based on each category
            - cluster similar reviews
            - rank and summarize amongst cluster to provide a summarize
    """
    # Read the app-config.json file.
    fawkes_config = FawkesConfig(utils.open_json(fawkes_config_file))
    # For every app registered in app-config.json we-
    for app_config_file in fawkes_config.apps:
        # Creating an AppConfig object
        app_config = AppConfig(utils.open_json(app_config_file))
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

        reviews = queries.getVocByCategory(reviews)
        summarized_reviews = {}

        # For each category, generate a summary
        for category in reviews:
            summarized_category_review = []

            # get reviews per category
            categorized_review = reviews[category]

            # Preprocess reviews
            sentences = preprocess_review(categorized_review)
            # number of sentences in a category should be atleast greater than
            # the number of clusters
            if (
                len(sentences)
                > app_config.algorithm_config.summarization.num_clusters - 1
            ):
                clustered_sentences = k_means_classification(
                    sentences, app_config.algorithm_config.summarization.num_clusters
                )
                for cluster in clustered_sentences.values():
                    if len(cluster) < constants.minimum_reviews_per_cluster:
                        continue
                    text = ". ".join(cluster)
                    gen_summary = summarize_text(
                        text,
                        app_config.algorithm_config.summarization.summary_length_per_cluster,
                    )
                    summarized_category_review.append(gen_summary)
            else:
                logging.info(logs.INSUFFICIENT_DATA, category)
            summarized_reviews[category] = summarized_category_review

        query_results_file_path = constants.REVIEW_SUMMARY_RESULTS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.query_folder,
            app_name=app_config.app.name,
        )

        dir_name = os.path.dirname(query_results_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        utils.dump_json(
            [{"summarized_reviews": summarized_reviews}], query_results_file_path
        )

        return summarized_reviews
