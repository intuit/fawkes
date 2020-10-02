# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sys
import pathlib

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
import fawkes.constants as constants

from fawkes.app_config.app_config import AppConfig, ReviewChannelTypes, CategorizationAlgorithms
from fawkes.review.review import Review

if __name__ == "__main__":
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

        # We get all the data.
        template_data = {
            "numberOfReview": queries.numberOfReview(reviews),
            "topCategory": queries.topCategory(reviews),
            "numFeatureReq": queries.numFeatureReq(reviews),
            "numBugsReported": queries.numBugsReported(reviews),
            "appStoreRating": "{0:.2f}".format(queries.appStoreRating(reviews)),
            "playStoreRating": "{0:.2f}".format(queries.playStoreRating(reviews)),
            "happyReview1": queries.happyReview1(reviews),
            "unhappyReview1": queries.unhappyReview1(reviews),
            "positiveReview": queries.positiveReview(reviews),
            "neutralReview": queries.neutralReview(reviews),
            "negativeReview": queries.negativeReview(reviews),
            "topCategoryNumberOfReview": queries.topCategoryNumberOfReview(reviews),
            "fromDate": queries.fromDate(reviews),
            "toDate": queries.toDate(reviews),
            "appLogo": app_config.app.logo,
            "timeSpanWords": app_config.email_config.email_time_span,
            "kibanaDashboardURL": app_config.elastic_config.kibana_url
        }

        # Get the initial HTML from the template file.
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
