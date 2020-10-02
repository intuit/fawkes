# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import sys
import pathlib

from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants as constants
from fawkes.app_config.app_config import AppConfig

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
        constants.APP_CONFIG_FILE.format(file_name=constants.APP_CONFIG_FILE_NAME)
    )
    for app_config_file in app_configs:
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
        # Path where the generated email in html format will be stored
        email_summary_generated_file_path = constants.EMAIL_SUMMARY_GENERATED_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.emails_folder,
            app_name=app_config.app.name,
        )

        dir_name = os.path.dirname(email_summary_generated_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        template_html = ""

        with open(email_summary_generated_file_path, "r") as email_file_handle:
            template_html = email_file_handle.read()

        for email_id in app_config.email_config.email_list:
            send_email_helper(app_config.email_config.sender_email_address, email_id,
                                app_config.email_config.email_subject_name, template_html,
                                app_config.email_config.sendgrid_api_key)
