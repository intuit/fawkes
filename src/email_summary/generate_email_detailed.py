# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sys
import functools

from pprint import pprint
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import src.utils as utils
from src.fetch_source_data.fetch_lifetime_ratings import *
from src.email_summary.email_utils import *
from src.email_summary.queries import *
from src.config import *


def compare_review_by_sentiment(review1, review2):
    return (review1[DERIVED_INSIGHTS][SENTIMENT][COMPOUND] -
            review2[DERIVED_INSIGHTS][SENTIMENT][COMPOUND])


def compare_review_by_category_score(review1, review2):
    category = review1[DERIVED_INSIGHTS][CATEGORY]
    # If the category has not been found, it will be "uncategorized"
    # All reviews in uncategorized have a score of 0
    # So we return True in such cases
    if category != CATEGORY_NOT_FOUND:
        return (review2[DERIVED_INSIGHTS][EXTRA_PROPERTIES][CATEGORY_SCORES]
                [category] - review1[DERIVED_INSIGHTS][EXTRA_PROPERTIES]
                [CATEGORY_SCORES][category])
    else:
        return True


if __name__ == "__main__":
    app_configs = utils.open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    # We process all algorithms on parsed data for each app
    # We process all algorithms on parsed data for each app
    for app in app_configs:
        print("[LOG] Processing : ", app)
        app_config = utils.open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if utils.validate_app_config(app_config):
            app_config = utils.decrypt_config(app_config)

            # Loading the REVIEW's
            reviews = utils.open_json(
                PROCESSED_INTEGRATED_REVIEW_FILE.format(
                    app_name=app_config[APP]))

            reviews = utils.filter_reviews(reviews, app_config, WEEKLY_SUMMARY)

            if len(reviews) == 0:
                continue

            review_by_category = getVocByCategory(reviews)

            top_categories = sorted([(len(review_by_category[key]), key)
                                     for key in review_by_category],
                                    reverse=True)

            top_categories = top_categories[:5]

            max_sentiment_per_category = {}

            for category in top_categories:
                max_sentiment_per_category[category[1]] = sorted(
                    review_by_category[category[1]],
                    key=functools.cmp_to_key(
                        compare_review_by_category_score))[0]

            reviewDivHTML = ""

            for category in top_categories:
                if category[1] == CATEGORY_NOT_FOUND:
                    continue
                template_data = {
                    "catetgoryName":
                        category[1],
                    "upOrDown":
                        "down",
                    "upDownPercentage":
                        19,
                    "reviewText":
                        max_sentiment_per_category[category[1]][MESSAGE],
                    "usersTalking":
                        len(review_by_category[category[1]])
                }

                formatted_html = generate_email(
                    WEEKLY_EMAIL_DETAILED_REVIEW_BLOCK_TEMPLATE, template_data)

                reviewDivHTML += formatted_html

            # We get all the data.
            template_data = {
                "appStoreRating":
                    "{0:.2f}".format(appStoreRating(reviews)),
                "playStoreRating":
                    "{0:.2f}".format(playStoreRating(reviews)),
                "positiveReview":
                    positiveReview(reviews),
                "neutralReview":
                    neutralReview(reviews),
                "negativeReview":
                    negativeReview(reviews),
                "fromDate":
                    fromDate(reviews),
                "toDate":
                    toDate(reviews),
                "appLogo":
                    app_config[APP_LOGO],
                "timeSpanWords":
                    app_config[EMAIL_TIME_SPAN_WORDS],
                "reviewBlock":
                    reviewDivHTML,
                "appStoreNumberOfReview":
                    appStoreNumberReview(reviews),
                "playStoreNumberOfReview":
                    playStoreNumberReview(reviews),
                "appStoreLifetimeRating":
                    getAppStoreLifetimeRating(app_config),
                "playStoreLifetimeRating":
                    getPlayStoreLifetimeRating(app_config),
                "kibanaDashboardURL":
                    app_config[KIBANA_DASHBOARD_URL]
            }

            # We finally send the email
            formatted_html = generate_email(WEEKLY_EMAIL_DETAILED_TEMPLATE,
                                            template_data)

            dir = DATA_DUMP_DIR

            fetch_file_save_path = PROCESSED_EMAIL_FILE.format(
                dir_name=dir, app_name=app_config[APP])

            with open(fetch_file_save_path, "w") as email_file_handle:
                email_file_handle.write(formatted_html)
