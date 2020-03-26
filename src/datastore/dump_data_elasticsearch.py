import requests
import sys
import os
import json
import random

from pprint import pprint

sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


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
    url = elastic_search_url + "/" + index + "/" + type + "/" + wid
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


def bulk_push_to_elastic(elastic_search_url, index, docs):
    """
    Format of bulk post to ElasticSearch
    POST _bulk
    { "index" : { "_index" : "test", "_type" : "_doc", "_id" : "1" } }
    { "field1" : "value1" }
    """
    CREATE_TEMPLATE = {"create": {"_index": index, "_type": "_doc", "_id": ""}}

    bulk_request_body = ""
    for doc in docs:
        CREATE_TEMPLATE["create"]["_id"] = doc[HASH_ID]
        bulk_request_body += json.dumps(CREATE_TEMPLATE) + NEW_LINE
        bulk_request_body += json.dumps(doc) + NEW_LINE

    # Request
    headers = {"content-type": "application/x-ndjson"}

    url = elastic_search_url + "/" + "_bulk"

    response = requests.post(url, data=bulk_request_body, headers=headers)
    return response


def push_data_to_elasticsearch():
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))
    for app in app_configs:
        app_config = open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if not validate_app_config(app_config):
            return
        app_config = decrypt_config(app_config)
        print("[LOG]:: dumpdata ", app_config["app"])
        # Load the file
        reviews = open_json(
            PROCESSED_INTEGRATED_REVIEW_FILE.format(app_name=app_config[APP]))

        reviews = [review for review in reviews if review["timestamp"] != ""]

        random.shuffle(reviews)

        print(
            "[LOG] push_data_to_elasticsearch :: Filtered using timestamp :: ",
            len(reviews))

        # We first list out all the indices
        indices = get_indices(app_config[ELASTIC_SEARCH_URL])
        if app_config[ELASTIC_SEARCH_INDEX_KEY] not in indices:
            print("[LOG] push_data_to_elasticsearch :: Creating a new index",
                  app_config[ELASTIC_SEARCH_INDEX_KEY])
            # Create a new index
            create_index(app_config[ELASTIC_SEARCH_URL],
                         app_config[ELASTIC_SEARCH_INDEX_KEY])

        # Bulk push the data
        i = 0
        while i * BULK_UPLOAD_SIZE < len(reviews):
            response = bulk_push_to_elastic(
                app_config[ELASTIC_SEARCH_URL],
                app_config[ELASTIC_SEARCH_INDEX_KEY],
                reviews[i *
                        BULK_UPLOAD_SIZE:min((i + 1) *
                                             BULK_UPLOAD_SIZE, len(reviews))])
            if response.status_code != 200:
                print(
                    "[Error] push_data_to_elasticsearch :: Got status code : ",
                    response.status_code)
                print("[Error] push_data_to_elasticsearch :: Response is : ",
                      response.text)
            i += 1


if __name__ == "__main__":
    push_data_to_elasticsearch()
