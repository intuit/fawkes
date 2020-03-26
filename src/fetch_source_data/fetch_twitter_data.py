import os
import sys
import twitter

from pprint import pprint
from datetime import datetime

# This is so that below import works
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *


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
                           language=TWITTER_QUERY_LANGUAGE,
                           count=100):
    # What handle to search
    query = "q=%40{handle}".format(handle=handle)

    # Adding parameter for only extracting only english tweets
    query += AMPERSAND + "lang={language}".format(language=language)

    # Adding the count. (default = 15).max to 100 per page
    query += AMPERSAND + "count={count}".format(count=count)

    # Adding date. Extracts tweets before given date. Date Format : YYYY-MM-DD
    # query += AMPERSAND + "until={until}".format(until=date)

    # Adding max_id to extract next page in twitter timeline pages
    if latest_id is not None:
        query += AMPERSAND + "max_id={id_num}".format(id_num=latest_id)

    # URL encode it
    return api.GetSearch(raw_query=query, return_json=True)


def fetch_from_twitter(twitter_config, app):

    api = twitter_authenthication(twitter_config[CONSUMER_KEY],
                                  twitter_config[CONSUMER_SECRET],
                                  twitter_config[ACCESS_TOKEN_KEY],
                                  twitter_config[ACCESS_TOKEN_SECRET])

    all_tweets = []
    for twitter_handle in twitter_config[TWITTER_HANDLE_LIST]:
        # Fetch the first page of the timeline TODO: for handlelist
        query_results = search_handle_mentions(
            api, twitter_handle,
            datetime.today().strftime("%Y-%m-%d"))

        # We iterate the twitter timeline pages to extract all the tweets for
        # the given query.
        while (len(query_results[KEY_CONTAINING_TWEETS]) > 0):
            all_tweets.extend(query_results[KEY_CONTAINING_TWEETS])
            latest_id = query_results[KEY_CONTAINING_TWEETS][-1][
                KEY_WITH_STATUS_ID] - 1
            query_results = search_handle_mentions(
                api, twitter_handle,
                datetime.today().strftime("%Y-%m-%d"), latest_id)

    dir = DATA_DUMP_DIR

    fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
        dir_name=dir,
        app_name=app,
        channel_name=twitter_config[CHANNEL_NAME],
        extension="json")
    # Creates directory on given path
    if not os.path.exists(dir):
        os.makedirs(dir)
    corrected_tweets = []
    for tweet in all_tweets:
        # We have to format the time so that later our parse functions can pick it up
        # We show mercy to Rabbits
        time = tweet[twitter_config[TIMESTAMP_KEY]].split(" ")
        del time[-2]
        tweet[twitter_config[TIMESTAMP_KEY]] = convert_date_format(
            " ".join(time))
        corrected_tweets.append(tweet)

    dump_json(corrected_tweets, fetch_file_save_path)
