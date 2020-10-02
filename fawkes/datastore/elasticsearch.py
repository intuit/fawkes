import requests
import sys
import os
import json
import random

from pprint import pprint
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.utils.filter_utils as filter_utils
import fawkes.constants as constants

from fawkes.app_config.app_config import AppConfig
from fawkes.review.review import Review

def create_index(elastic_search_url, index):
    response = requests.put(elastic_search_url + "/" + index)
    return response


def get_indices(elastic_search_url):
    headers = {"content-type": "application/json"}
    response = requests.get(elastic_search_url + "/_cat/indices?v",
                            headers=headers)

    # Don"t know who made this as a text based API
    indices = response.text.split("\n")

    # We split the row for each index by space, but there are multiple spaces
    # so we join them and split again.
    indices = [" ".join(index.split()).split() for index in indices]

    # We return the list of indices
    return [index[2] for index in indices if len(index) > 2]


def create_document(elastic_search_url, index, type, id, document):
    headers = {"content-type": "application/json"}
    url = elastic_search_url + "/" + index + "/" + type + "/" + str(id)
    response = requests.put(url, data=json.dumps(document), headers=headers)
    return response


def get_document(elastic_search_url, index, type, id):
    url = elastic_search_url + "/" + index + "/" + type + "/" + id
    response = requests.get(url)
    return response


def delete_index(elastic_search_url, index):
    response = requests.delete(elastic_search_url + "/" + index)
    return response


def delete_document(elastic_search_url, index, type, id):
    headers = {"content-type": "application/json"}
    url = elastic_search_url + "/" + index + "/" + type + "/" + id
    response = requests.delete(url)
    return response


def bulk_push_to_elastic(elastic_search_url, index, reviews):
    """
    Format of bulk post to ElasticSearch
    POST _bulk
    { "index" : { "_index" : "test", "_type" : "_doc", "_id" : "1" } }
    { "field1" : "value1" }
    """
    create_template = {"create": {"_index": index, "_type": "_doc", "_id": ""}}

    bulk_request_body = ""
    for review in reviews:
        create_template["create"]["_id"] = review.hash_id
        bulk_request_body += json.dumps(create_template) + constants.NEW_LINE
        bulk_request_body += json.dumps(review.to_dict()) + constants.NEW_LINE

    # Request
    headers = {"content-type": "application/x-ndjson"}

    url = elastic_search_url + "/" + "_bulk"

    response = requests.post(url, data=bulk_request_body, headers=headers)
    return response


def push_data_to_elasticsearch():
    app_configs = utils.open_json(
        constants.APP_CONFIG_FILE.format(file_name=constants.APP_CONFIG_FILE_NAME)
    )
    for app_config_file in app_configs:
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
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
            datetime.now(timezone.utc) - timedelta(days=app_config.email_config.email_time_span)
        )

        # We shuffle the reviews. This is because of how elastic search.
        random.shuffle(reviews)

        # We first list out all the indices
        indices = get_indices(app_config.elastic_config.elastic_search_url)
        if app_config.elastic_config.index not in indices:
            # Create a new index
            create_index(app_config.elastic_config.elastic_search_url,
                         app_config.elastic_config.index)

        # Bulk push the data
        i = 0
        while i * constants.BULK_UPLOAD_SIZE < len(reviews):
            response = bulk_push_to_elastic(
                app_config.elastic_config.elastic_search_url,
                app_config.elastic_config.index,
                reviews[i *
                        constants.BULK_UPLOAD_SIZE:min((i + 1) *
                                             constants.BULK_UPLOAD_SIZE, len(reviews))])
            if response.status_code != 200:
                print(
                    "[Error] push_data_to_elasticsearch :: Got status code : ",
                    response.status_code)
                print("[Error] push_data_to_elasticsearch :: Response is : ",
                      response.text)
            i += 1


if __name__ == "__main__":
    push_data_to_elasticsearch()
