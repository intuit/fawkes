import os
import sys
import requests
import json

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


def get_oauth_token(base_url, params):

    url = base_url + "/services/oauth2/token"

    response = requests.post(url, params=params)

    return json.loads(response.text)


def get_query_results(base_url, bearer_token, query):

    url = base_url + "/services/data/v37.0/query"

    headers = {"Authorization": "Bearer " + bearer_token}

    url += "?q=" + query.format(days=SALESFORCE_EXTRACTION_DAYS)
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def get_next_page(url, bearer_token):
    """ Get remaining pages of the query """
    headers = {"Authorization": "Bearer " + bearer_token}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def fetch_from_salesforce(salesforce_details, app):
    # Authenticate with salesforce api
    token_response = get_oauth_token(
        salesforce_details[SALESFORCE_BASE_URL],
        salesforce_details[SALESFORCE_OAUTH_PARAMS])

    data = []
    records = []

    # Fetch the results of query
    for query in salesforce_details[SALESFORCE_QUERY_LIST]:
        data = (get_query_results(salesforce_details[SALESFORCE_BASE_URL],
                                  token_response[SALESFORCE_ACCESS_TOKEN_KEY],
                                  query))

        # Data returned has format :
        # "nextRecordsUrl" : next page url
        # "done" : true if end of the page is reached
        # "records" : actual query results
        records = data[RECORDS]

        # Get all the pages returned for the query
        while (SALESFORCE_PAGINATION_URL in data) and (not data[DONE]):
            data = get_next_page(
                salesforce_details[SALESFORCE_BASE_URL] +
                data[SALESFORCE_PAGINATION_URL],
                token_response[SALESFORCE_ACCESS_TOKEN_KEY])
            records += data[RECORDS]

        dir = DATA_DUMP_DIR

        # If there is one query , file nomeclature changes
        if len(salesforce_details[SALESFORCE_QUERY_LIST]) > 1:
            file_suffix = "-" + \
                str(salesforce_details[SALESFORCE_QUERY_LIST].index(query))
        else:
            file_suffix = ""

        fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
            dir_name=dir,
            app_name=app,
            channel_name=salesforce_details[CHANNEL_NAME] + file_suffix,
            extension="json")

        # Get the value of timestamp and message
        for i in range(len(records)):
            if salesforce_details[TIMESTAMP_KEY] in records[i]:
                records[i][salesforce_details[TIMESTAMP_KEY]] = records[i][
                    salesforce_details[TIMESTAMP_KEY]].split("T")[0]

        if not os.path.exists(dir):
            os.makedirs(dir)

        dump_json(records, fetch_file_save_path)
