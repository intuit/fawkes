import os
import sys
import json
import requests
import time
import urllib

from pprint import pprint
from datetime import datetime

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import src.utils as utils

from src.config import *


def generate_star_from_rating(rating):
    return "".join(["★" for i in range(rating)])


def get_rating_color(rating):
    if rating > 3:
        return "good"
    elif rating < 3:
        return "danger"
    return "warning"


def get_sentiment_color(sentiment):
    if sentiment > 0:
        return "good"
    elif sentiment < 0:
        return "danger"
    return "warning"


def get_jira_details(review, app_config, issue_type):
    # We give a generic summary with just the category of the message.
    summary = "REVIEW Feeback on : {category}".format(
        category=review[DERIVED_INSIGHTS][CATEGORY])

    # Description will have the REVIEW followed by the unified json dump.
    description = review[MESSAGE]
    description = review[MESSAGE] + \
        "\n\n Details : \n {code:json}" + json.dumps(review, indent=4) + "{code}"

    # We take the issue type and the project id from the user
    issuetype = app_config[JIRA][issue_type]
    pid = app_config[JIRA][PROJECT_ID]

    params = {
        "summary": summary,
        "description": description,
        "issuetype": issuetype,
        "pid": pid,
        "labels": "Fawkes"
    }

    params_enc = urllib.parse.urlencode(params)

    return JIRA_ISSUE_URL_TEMPLATE.format(
        params=params_enc, base_url=app_config[JIRA][JIRA_BASE_URL])


def get_actions(review, app_config):
    text = "Create Story"
    issue_type = STORY_ISSUE_TYPE
    if review[DERIVED_INSIGHTS][EXTRA_PROPERTIES][BUG_FEATURE] == BUG:
        text = "Report a Bug"
        issue_type = BUG_ISSSUE_TYPE
    elif review[DERIVED_INSIGHTS][EXTRA_PROPERTIES][BUG_FEATURE] == FEATURE:
        text = "Request a Feature"
    return [{
        "type": "button",
        "text": text,
        "url": get_jira_details(review, app_config, issue_type),
        "style": "primary"
    }]


def get_people_to_tag(app_config, review):
    list_of_slack_ids = []
    if SLACK_TAGS in app_config:
        if CATEGORY in app_config[SLACK_TAGS]:
            # Adding all the people who have subscribed to
            if review[DERIVED_INSIGHTS][CATEGORY] in app_config[SLACK_TAGS][
                    CATEGORY]:
                list_of_slack_ids += app_config[SLACK_TAGS][CATEGORY][
                    review[DERIVED_INSIGHTS][CATEGORY]]
        # Now adding people who have subscribed to keywords
        if SLACK_KEYWORDS in app_config[SLACK_TAGS]:
            for keyword in app_config[SLACK_TAGS][SLACK_KEYWORDS]:
                if keyword in review[MESSAGE]:
                    list_of_slack_ids += app_config[SLACK_TAGS][SLACK_KEYWORDS][
                        keyword]
    return list_of_slack_ids


def send_to_slack(slack_url,
                  slack_channel,
                  review,
                  app_config,
                  isUnifiedJSON=True):
    """
    Function to send things to slack.
    Takes a unified json and sends it to slack.
    If overridden, then treats the payload as text and sends to slack.
    """
    payload = {
        "channel": slack_channel,
    }
    headers = {'content-type': 'application/json'}

    # We don't want to send empty message to slack.
    if review[MESSAGE] == "" or review[MESSAGE] == "NA":
        return

    # If its a text, we just send it.
    if not isUnifiedJSON:
        payload = {"channel": slack_channel, "text": review}
    else:
        attachments = []
        user_mention_list = get_people_to_tag(app_config, review)
        user_mention_string = " ".join(
            "<" + str(user) + ">" for user in user_mention_list)
        # We create the attachment payload
        attachment = {
            "fallback":
                review[MESSAGE],
            "color":
                get_sentiment_color(
                    review[DERIVED_INSIGHTS][SENTIMENT][COMPOUND]),
            "pretext":
                "Sentiment : " +
                str(review[DERIVED_INSIGHTS][SENTIMENT][COMPOUND]),
            "author_name":
                review[DERIVED_INSIGHTS][CATEGORY],
            "author_link":
                "search-fawkes-e2e-obimwlpxmz7dnwz4owke6jmvy4.us-west-2.es.amazonaws.com/_plugin/kibana/app/kibana",
            "author_icon":
                "https://i.imgur.com/pydBDO7.png",
            "text":
                review[MESSAGE] + SPACE + user_mention_string,
            "ts":
                time.mktime(
                    datetime.strptime(review[TIMESTAMP],
                                      '%Y/%m/%d %H:%M:%S').timetuple()),
            "footer":
                review[APP] + " : " + review[CHANNEL_TYPE],
            "actions":
                get_actions(review, app_config)
        }

        # Twitter
        if review[CHANNEL_TYPE] == CHANNEL_NAME_TWITTER:
            # Extract the tweet URL and send it
            payload["text"] = TWITTER_URL.format(
                status_id=review[PROPERTIES]["id_str"])

            # Send the request to slack
            response = requests.post(slack_url,
                                     data=json.dumps(payload),
                                     headers=headers)

            return

        # App Store and Play Store
        elif RATING in review[PROPERTIES]:
            # attachment["color"] = get_rating_color(review[PROPERTIES][RATING])
            attachment["pretext"] = generate_star_from_rating(
                review[PROPERTIES][RATING])

        attachments.append(attachment)
        payload["attachments"] = attachments

    # Send the request to slack
    response = requests.post(slack_url,
                             data=json.dumps(payload),
                             headers=headers)


if __name__ == "__main__":
    app_configs = utils.open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    # We process all algorithms on parsed data for each app
    for app in app_configs:
        app_config = utils.open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if utils.validate_app_config(app_config):
            app_config = utils.decrypt_config(app_config)

            # Loading the REVIEW's
            reviews = utils.open_json(
                PROCESSED_INTEGRATED_REVIEW_FILE.format(
                    app_name=app_config[APP]))

            reviews = utils.filter_reviews(reviews, app_config)

            reviews = utils.filter_review_for_slack(reviews, app_config)

            reviews = sorted(reviews,
                             key=lambda review: review[DERIVED_INSIGHTS][
                                 SENTIMENT][COMPOUND],
                             reverse=True)

            for review in reviews:
                send_to_slack(app_config[SLACK_HOOK_URL],
                              app_config[SLACK_CHANNEL_NAME], review,
                              app_config)
