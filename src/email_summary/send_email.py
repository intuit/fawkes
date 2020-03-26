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

from src.email_summary.queries import *
from src.config import *


def send_email_helper(from_email_address, to_email, subject, html,
                      sendgrid_api_key):
    message = Mail(from_email=from_email_address,
                   to_emails=to_email,
                   subject=subject,
                   html_content=html)
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print("[LOG] Email to ", to_email, response.status_code)
    except Exception as e:
        print(e.message)


if __name__ == "__main__":
    app_configs = utils.open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    # We process all algorithms on parsed data for each app
    # We process all algorithms on parsed data for each app
    for app in app_configs:
        app_config = utils.open_json(APP_CONFIG_FILE.format(file_name=app))
        # If the app json schema is not valid, we don't execute any thing.
        if utils.validate_app_config(app_config):
            app_config = utils.decrypt_config(app_config)

            dir = DATA_DUMP_DIR

            fetch_file_save_path = PROCESSED_EMAIL_FILE.format(
                dir_name=dir, app_name=app_config[APP])

            with open(fetch_file_save_path, "r") as email_file_handle:
                template_html = email_file_handle.read()

            for email_id in app_config[EMAIL_LIST]:
                send_email_helper(app_config[SENDER_EMAIL_ADDRESS], email_id,
                                  app_config[EMAIL_SUBJECT_NAME], template_html,
                                  app_config[SENDGRID_API_KEY])
