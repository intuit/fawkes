import os
import sys
import functools
import pathlib

from pprint import pprint
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta, timezone

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.email_summary.email_utils as email_utils
import fawkes.email_summary.queries as queries

import fawkes.utils.utils as utils
import fawkes.utils.filter_utils as filter_utils
import fawkes.constants.constants as constants
import fawkes.fetch.lifetime as lifetime

from fawkes.configs.app_config import AppConfig, ReviewChannelTypes, CategorizationAlgorithms
from fawkes.configs.fawkes_config import FawkesConfig
from fawkes.review.review import Review

def compare_review_by_sentiment(review1, review2):
    return (review1.derived_insight.sentiment["compound"] -
            review2.derived_insight.sentiment["compound"])


def compare_review_by_category_score(review1, review2):
    category = review1.derived_insight.category
    # If the category has not been found, it will be "uncategorized"
    # All reviews in uncategorized have a score of 0
    # So we return True in such cases
    if category != constants.CATEGORY_NOT_FOUND:
        return (review2.derived_insight.extra_properties[constants.CATEGORY_SCORES][category] - review1.derived_insight.extra_properties[constants.CATEGORY_SCORES][category])
    else:
        return True


def generate_email_summary_detailed(fawkes_config_file = constants.FAWKES_CONFIG_FILE):
    # Read the app-config.json file.
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
        if len(reviews) == 0:
            continue

        review_by_category = queries.getVocByCategory(reviews)

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
            if category[1] == constants.CATEGORY_NOT_FOUND:
                continue
            template_data = {
                "catetgoryName":
                    category[1],
                "upOrDown":
                    "down",
                "upDownPercentage":
                    19,
                "reviewText":
                    max_sentiment_per_category[category[1]].message,
                "usersTalking":
                    len(review_by_category[category[1]])
            }

            formatted_html = email_utils.generate_email(
                constants.WEEKLY_EMAIL_DETAILED_REVIEW_BLOCK_TEMPLATE,
                template_data
            )


            reviewDivHTML += formatted_html

        # We get all the data.
        template_data = {
            "appStoreRating":
                "{0:.2f}".format(queries.appStoreRating(reviews)),
            "playStoreRating":
                "{0:.2f}".format(queries.playStoreRating(reviews)),
            "positiveReview":
                queries.positiveReview(reviews),
            "neutralReview":
                queries.neutralReview(reviews),
            "negativeReview":
                queries.negativeReview(reviews),
            "fromDate":
                queries.fromDate(reviews),
            "toDate":
                queries.toDate(reviews),
            "appLogo":
                app_config.app.logo,
            "timeSpanWords":
                app_config.email_config.email_time_span_in_words,
            "reviewBlock":
                reviewDivHTML,
            "appStoreNumberOfReview":
                queries.appStoreNumberReview(reviews),
            "playStoreNumberOfReview":
                queries.playStoreNumberReview(reviews),
            "appStoreLifetimeRating":
                lifetime.getAppStoreLifetimeRating(app_config),
            "playStoreLifetimeRating":
                lifetime.getPlayStoreLifetimeRating(app_config),
            "kibanaDashboardURL":
                app_config.elastic_config.kibana_url
        }

        # We finally send the email
        formatted_html = email_utils.generate_email(
            app_config.email_config.email_template_file,
            template_data
        )

        # Path where the generated email in html format will be stored
        email_summary_generated_file_path = constants.EMAIL_SUMMARY_GENERATED_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.emails_folder,
            app_name=app_config.app.name,
        )

        dir_name = os.path.dirname(email_summary_generated_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        with open(email_summary_generated_file_path, "w") as email_file_handle:
            email_file_handle.write(formatted_html)
