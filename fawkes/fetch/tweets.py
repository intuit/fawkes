import os
import sys
import twitter

from pprint import pprint
from datetime import datetime

# This is so that below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

def twitter_authenthication(consumer_key, consumer_secret, access_token_key,
                            access_token_secret):
    return twitter.Api(consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token_key=access_token_key,
                       access_token_secret=access_token_secret)


def search_handle_mentions(api,
                           handle,
                           date,
                           latest_id=None,
                           language=constants.TWITTER_QUERY_LANGUAGE,
                           count=100):
    # What handle to search
    query = "q=%40{handle}".format(handle=handle)

    # Adding parameter for only extracting only english tweets
    query += constants.AMPERSAND + "lang={language}".format(language=language)

    # Adding the count. (default = 15).max to 100 per page
    query += constants.AMPERSAND + "count={count}".format(count=count)

    # Adding date. Extracts tweets before given date. Date Format : YYYY-MM-DD
    # query += AMPERSAND + "until={until}".format(until=date)

    # Adding max_id to extract next page in twitter timeline pages
    if latest_id is not None:
        query += constants.AMPERSAND + "max_id={id_num}".format(id_num=latest_id)

    # URL encode it
    return api.GetSearch(raw_query=query, return_json=True)


def fetch(review_channel):
    api = twitter_authenthication(review_channel.consumer_key,
                                  review_channel.consumer_secret,
                                  review_channel.access_token_key,
                                  review_channel.access_token_secret)

    all_tweets = []
    for twitter_handle in review_channel.twitter_handle_list:
        # Fetch the first page of the timeline
        query_results = search_handle_mentions(
            api, twitter_handle,
            datetime.today().strftime("%Y-%m-%d"))

        # We iterate the twitter timeline pages to extract all the tweets for
        # the given query.
        while (len(query_results[constants.KEY_CONTAINING_TWEETS]) > 0):
            all_tweets.extend(query_results[constants.KEY_CONTAINING_TWEETS])
            latest_id = query_results[constants.KEY_CONTAINING_TWEETS][-1][
                constants.KEY_WITH_STATUS_ID] - 1
            query_results = search_handle_mentions(
                api, twitter_handle,
                datetime.today().strftime("%Y-%m-%d"), latest_id)

    return all_tweets
