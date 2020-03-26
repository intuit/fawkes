# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sys
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import src.utils as utils
from src.email_summary.email_utils import *
from src.email_summary.queries import *
from src.config import *

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

            # We get all the data.
            template_data = {
                "numberOfReview": numberOfReview(reviews),
                "topCategory": topCategory(reviews),
                "numFeatureReq": numFeatureReq(reviews),
                "numBugsReported": numBugsReported(reviews),
                "appStoreRating": "{0:.2f}".format(appStoreRating(reviews)),
                "playStoreRating": "{0:.2f}".format(playStoreRating(reviews)),
                "happyReview1": happyReview1(reviews),
                "unhappyReview1": unhappyReview1(reviews),
                "positiveReview": positiveReview(reviews),
                "neutralReview": neutralReview(reviews),
                "negativeReview": negativeReview(reviews),
                "topCategoryNumberOfReview": topCategoryNumberOfReview(reviews),
                "fromDate": fromDate(reviews),
                "toDate": toDate(reviews),
                "appLogo": app_config[APP_LOGO],
                "timeSpanWords": app_config[EMAIL_TIME_SPAN_WORDS],
                "kibanaDashboardURL": app_config[KIBANA_DASHBOARD_URL]
            }

            # We finally send the email
            formatted_html = generate_email(WEEKLY_EMAIL_TEMPLATE,
                                            template_data)

            dir = DATA_DUMP_DIR

            fetch_file_save_path = PROCESSED_EMAIL_FILE.format(
                dir_name=dir, app_name=app_config[APP])

            with open(fetch_file_save_path, "w") as email_file_handle:
                email_file_handle.write(formatted_html)
