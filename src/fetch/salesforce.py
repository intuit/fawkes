import os
import sys
import requests
import json

from pprint import pprint

# This is so that below import works
sys.path.append(os.path.realpath("."))

import src.utils.utils as utils
import src.constants as constants


def get_oauth_token(base_url, params):

    url = base_url + "/services/oauth2/token"

    response = requests.post(url, params=params)

    return json.loads(response.text)


def get_query_results(base_url, bearer_token, query):

    url = base_url + "/services/data/v37.0/query"

    headers = {"Authorization": "Bearer " + bearer_token}

    url += "?q=" + query.format(days=constants.SALESFORCE_EXTRACTION_DAYS)
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def get_next_page(url, bearer_token):
    """ Get remaining pages of the query """
    headers = {"Authorization": "Bearer " + bearer_token}
    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def fetch(review_channel):
    # Authenticate with salesforce api
    token_response = get_oauth_token(
        salesforce_details.base_url,
        salesforce_details.oauth_params)

    data = []
    records = []

    # Fetch the results of query
    for query in salesforce_details.query_list:
        data = (get_query_results(salesforce_details.base_url,
                                  token_response[constants.SALESFORCE_ACCESS_TOKEN_KEY],
                                  query))

        # Data returned has format :
        # "nextRecordsUrl" : next page url
        # "done" : true if end of the page is reached
        # "records" : actual query results
        records = data[constants.RECORDS]

        # Get all the pages returned for the query
        while (constants.SALESFORCE_PAGINATION_URL in data) and (not data[constants.DONE]):
            data = get_next_page(
                salesforce_details.base_url +
                data[constants.SALESFORCE_PAGINATION_URL],
                token_response[constants.SALESFORCE_ACCESS_TOKEN_KEY])
            records += data[constants.RECORDS]

        # If there is one query , file nomeclature changes
        if len(salesforce_details.query_list) > 1:
            file_suffix = "-" + \
                str(salesforce_details.query_list.index(query))
        else:
            file_suffix = ""

        # Get the value of timestamp and message
        for i in range(len(records)):
            if salesforce_details.timestamp_key in records[i]:
                records[i][salesforce_details.timestamp_key] = records[i][
                    salesforce_details.timestamp_key].split("T")[0]
    return records