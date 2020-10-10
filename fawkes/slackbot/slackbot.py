import os
import sys
import json
import requests
import time
import urllib

from pprint import pprint
from datetime import datetime, timedelta, timezone

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants
import fawkes.utils.filter_utils as filter_utils

from fawkes.configs.app_config import AppConfig, ReviewChannelTypes
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review

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
        category=review.derived_insight.category)

    # Description will have the REVIEW followed by the unified json dump.
    description = review.message
    description = review.message + \
        "\n\n Details : \n {code:json}" + json.dumps(review.to_dict(), indent=4) + "{code}"

    # We take the issue type and the project id from the user
    if issue_type == constants.BUG:
        jira_issue_type = app_config.jira_config.bug_type
    else:
        jira_issue_type = app_config.jira_config.story_type

    pid = app_config.jira_config.project_id

    params = {
        "summary": summary,
        "description": description,
        "issuetype": jira_issue_type,
        "pid": pid,
        "labels": "Fawkes"
    }

    params_enc = urllib.parse.urlencode(params)

    return constants.JIRA_ISSUE_URL_TEMPLATE.format(
        params=params_enc, base_url=app_config.jira_config.base_url)


def get_actions(review, app_config):
    actions = []
    if constants.BUG_FEATURE in review.derived_insight.extra_properties:
        # Default Jira related stuff
        text = "Create Story"
        # Depending on tht type of the issue, whether its bug or story we have different actions.
        if review.derived_insight.extra_properties[constants.BUG_FEATURE] == constants.BUG:
            text = "Report a Bug"
        elif review.derived_insight.extra_properties[constants.BUG_FEATURE] == constants.FEATURE:
            text = "Request a Feature"
        # Append the action to the list of actions.
        actions.append({
            "type": "button",
            "text": text,
            "url": get_jira_details(
                review,
                app_config,
                review.derived_insight.extra_properties[constants.BUG_FEATURE]
            ),
            "style": "primary"
        })
    return actions


def get_people_to_tag(app_config, review):
    list_of_slack_ids = []
    if app_config.slack_config.slack_notification_rules.category_based_rules != None:
        # Adding all the people who have subscribed to a category
        if review.derived_insight.category in app_config.slack_config.slack_notification_rules.category_based_rules:
            list_of_slack_ids += app_config.slack_config.slack_notification_rules.category_based_rules[review.derived_insight.category]
    # Now adding people who have subscribed to keywords
    if app_config.slack_config.slack_notification_rules.keyword_based_rules != None:
        for keyword in app_config.slack_config.slack_notification_rules.keyword_based_rules:
            if keyword in review.message:
                list_of_slack_ids += app_config.slack_config.slack_notification_rules.keyword_based_rules[keyword]
    return list_of_slack_ids


def send_review_to_slack(slack_url,
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
    if review.message == "" or review.message == "NA":
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
                review.message,
            "color":
                get_sentiment_color(
                    review.derived_insight.sentiment["compound"]),
            "pretext":
                "Sentiment : " +
                str(review.derived_insight.sentiment["compound"]),
            "author_name":
                review.derived_insight.category,
            "author_link":
                "",
            "author_icon":
                "https://i.imgur.com/pydBDO7.png",
            "text":
                review.message + constants.SPACE + user_mention_string,
            "ts":
                time.mktime(
                    review.timestamp.timetuple()
                ),
            "footer":
                review.app_name + " : " + review.channel_type,
            "actions":
                get_actions(review, app_config)
        }

        # Twitter
        if review.channel_type == ReviewChannelTypes.TWITTER:
            # Extract the tweet URL and send it
            payload["text"] = constants.TWITTER_URL.format(
                status_id=review.raw_review["id_str"]
            )

            # Send the request to slack
            response = requests.post(
                slack_url,
                data=json.dumps(payload),
                headers=headers
            )

            return

        # App Store and Play Store
        elif review.rating != None:
            attachment["pretext"] = generate_star_from_rating(
                review.rating)

        attachments.append(attachment)
        payload["attachments"] = attachments

    # Send the request to slack
    response = requests.post(slack_url,
                             data=json.dumps(payload),
                             headers=headers)


def send_reviews_to_slack(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
   ## Read the app-config.json file.
    fawkes_config = FawkesConfig(
        utils.open_json(fawkes_config_file)
    )
    # For every app registered in app-config.json we
    for app_config_file in fawkes_config.apps:
        # Creating an AppConfig object
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )

        # Create the intermediate folders
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
            datetime.now(timezone.utc) - timedelta(minutes=app_config.slack_config.slack_run_interval)
        )

        reviews = sorted(reviews,
                            key=lambda review: review.derived_insight.sentiment["compound"],
                            reverse=True)

        for review in reviews:
            send_review_to_slack(app_config.slack_config.slack_hook_url,
                            app_config.slack_config.slack_channel, review,
                            app_config)

