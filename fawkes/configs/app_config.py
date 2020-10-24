import json
import os
from pprint import pprint
import sys
import jsonschema
from jsonschema import ValidationError

sys.path.append(os.path.realpath("."))

import fawkes.constants.constants as constants
import fawkes.utils.utils as utils

class App:
    """ The App in the App Config. Contains the application level properties.

    Attributes:
        name: The name of the application.
        logo: The logo url of the application.
    """

    def __init__(self, config):
        self.name = config["name"]
        self.logo = config["logo"]

class ElasticConfig:
    """ The configurations required for ElasticSearch and Kibana.

    Attributes:
        index: The index name where all the data goes in elastic search.
        elastic_search_url: The url for elastic search instance.
        kibana_url: The kibana dashboard url.
        lifetime_rating_index:
            A separate index has to be create for pushing the lifetime ratings of the user reviews.
            This is because lifetime rating differs from the usual user review itself.
    """

    def __init__(self, config):
        self.index = config["index"]
        self.elastic_search_url = config["elastic_search_url"]
        self.kibana_url = config["kibana_url"]
        self.lifetime_rating_index = config["lifetime_rating_index"]

class EmailConfig:
    """ The configurations required for sending an email summary from fawkes.

    Attributes:
        email_template_file: The template file to be used for the email summary.
        email_time_span: The time filter in days to be used for filtering the user review for the email summary.
        email_time_span_in_words: The time filter in words to be used as a string in the email summary.
        email_subject_name: The subject of the email summary.
        sender_email_address: The email address from which the email will be sent.
        email_list: The list of email address to which the email is sent.
        sendgrid_api_key: The sendgrid api key. https://sendgrid.com/
    """

    def __init__(self, config):
        self.email_template_file = config["email_template_file"]
        self.email_time_span = config["email_time_span"]
        self.email_time_span_in_words = config["email_time_span_in_words"]
        self.email_subject_name = config["email_subject_name"]
        self.sender_email_address = config["sender_email_address"]
        self.email_list = config["email_list"]
        self.sendgrid_api_key = config["sendgrid_api_key"]

class SlackCustomNotifications:
    """ The configurations required for triggering custom notifications to users on slack based on categories and keyword phrases which match.

    Attributes:
        category_based_rules: A dictionary with category names as keys and list of slack username's to be notified as values.
        keyword_based_rules: A dictionary with keywords as keys and list of slack username's to be notified as values.
    """

    def __init__(self, config):
        self.category_based_rules = config["category_based_rules"]
        self.keyword_based_rules = config["keyword_based_rules"]

class SlackConfig:
    """ The configurations required for sending user reviews to slack and triggering custom notifications.

    Attributes:
        slack_channel: The slack channel to send the user reviews to.
        slack_hook_url: The web-hook url to be used to send the user reviews.
        slack_run_interval: The time interval in minutes to filter the user reviews before sending to slack.
        slack_notification_rules: Custom notification rules for users who want to subscribe to certain keywords or categories.
    """

    def __init__(self, config):
        self.slack_channel = config["slack_channel"]
        self.slack_hook_url = config["slack_hook_url"]
        self.slack_run_interval = config["slack_run_interval"]
        self.slack_notification_rules = SlackCustomNotifications(config["slack_notification_rules"])

class JiraConfig:
    """ The configurations required to add Jira related information in the slack notification.

    Attributes:
        base_url:
            The base url for the jira hosting. An issue should look like this https://<base_url>/browse/<project_id>-<issue_number>
        project_id: The project id
        story_type: The numeric id mapped in the project(mentioned above) for a story
        bug_type: The numeric id mapped in the project(mentioned above) for a bug
    """

    def __init__(self, config):
        self.base_url = config["base_url"]
        self.project_id = config["project_id"]
        self.story_type = config["story_type"]
        self.bug_type = config["bug_type"]

class CategorizationAlgorithms:
    TEXT_MATCH_CLASSIFICATION = "text_match"
    LSTM_CLASSIFICATION = "lstm_classification"

class AlgorithmConfig:
    """  The configurations required for running algorithms.

    Attributes:
        categorization_algorithm: The categorisation algorithm to use to categorise the user reviews.
        algorithm_days_filter: The time filter in days to be used for filtering the user review for running the algorithms.
        bug_feature_keywords_file: The file path to the keywords for bug-feature categorisation.
        bug_feature_keywords_weights_file:  The file path to the keywords with weights for bug-feature categorisation.
        category_keywords_file: The file path to the keywords for categorisation.
        category_keywords_weights_file: The file path to the keywords with weights for categorisation.
    """

    def __init__(self, config):
        self.categorization_algorithm = config["categorization_algorithm"]
        self.algorithm_days_filter = config["algorithm_days_filter"]
        self.bug_feature_keywords_file = config["bug_feature_keywords_file"]
        self.bug_feature_keywords_weights_file = config["bug_feature_keywords_weights_file"]
        self.category_keywords_file = config["category_keywords_file"]
        self.category_keywords_weights_file = config["category_keywords_weights_file"]


class ReviewChannelTypes:
    IOS = "ios"
    ANDROID = "android"
    SPREADSHEET = "spreadsheet"
    TWITTER = "twitter"
    SALESFORCE = "salesforce"
    CSV = "csv"
    JSON = "json"
    BLANK = "blank"
    REMOTE_FILE = "remote_file"

class ReviewChannel:
    """ Definition of a Review Channel.

    ReviewChannel is the base class for all the review channel types.
    Review Channels are sources from which user reviews are extracted.
    These can be any source which provides it though an API or eve a raw csv or json file.

    Attributes:
        channel_type: The type pf channel from which the user review is fetched. See ReviewChannelTypes for more info.
        channel_name: The name of the review channel.
        file_type: The type of file that the review channel generates. Can be either json or csv.
        file_path: The path to the file if its a local file. Should be null for API based review channels.
        is_channel_enabled: Indicated whether the channel is enabled or not.
        timestamp_key: The key in the json/csv where the timestamp of the user review can be found.
        timestamp_format: The format in which the timestamp is present in the user review source.
        timezone: The timezone in which the user review is in.
        message_key: The key in the json/csv where the message of the user review can be found.
        rating_key: The key in the json/csv where the rating of the user review can be found.
    """

    def __init__(self, config):
        self.channel_type = config["channel_type"]
        self.channel_name = config["channel_name"]
        self.file_type = config["file_type"]
        self.file_path = config["file_path"]
        self.is_channel_enabled = config["is_channel_enabled"]
        self.timestamp_key = config["timestamp_key"]
        self.timestamp_format = config["timestamp_format"]
        self.timezone = config["timezone"]
        self.message_key = config["message_key"]
        self.rating_key = config["rating_key"]

class AppStoreReviewChannel(ReviewChannel):
    """ The configurations specific to App. Store.

    Attributes:
        app_id:
            The app id in the App. Store.
            Example for mint. https://apps.apple.com/us/app/mint-personal-finance-money/id300238550
            The app_id here is 300238550.
        country: The country for which you want to retrieve the user reviews.
    """

    def __init__(self, config):
        super().__init__(config)
        self.app_id = config["app_id"]
        self.country = config["country"]

        # Pre defined constants for App. Store.
        self.timestamp_key = "updated"
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
        self.message_key = "content"
        self.rating_key = "rating"

class PlayStoreReviewChannel(ReviewChannel):
    """ The configurations specific to App. Store.

    Attributes:
        app_id:
            The app id in the Play Store.
            Example for mint. https://play.google.com/store/apps/details?id=com.mint&hl=en
            The app_id here is com.mint.
        searchman_api_key: A list of api key's for searchman. https://searchman.com/
    """

    def __init__(self, config):
        super().__init__(config)
        self.app_id = config["app_id"]
        self.searchman_api_key = config["searchman_api_key"]

        # Pre defined constants for Play. Store.
        self.timestamp_key = "timestamp"
        self.message_key = "content"

class TwitterReviewChannel(ReviewChannel):
    """ The configurations specific to Twitter.

    Attributes:
        consumer_key: The consumer key for the twitter api.
        consumer_secret: The consumer secret for the twitter api.
        access_token_key: The access token key for the twitter api.
        access_token_secret: The access toekn secret for the twitter api.
        twitter_handle_list: The list of twitter handles to fetch the tweets from.
        twitter_handle_filter_list: The list of twiiter handle mentions to filter if present in the tweet.
    """

    def __init__(self, config):
        super().__init__(config)
        self.consumer_key = config["consumer_key"]
        self.consumer_secret = config["consumer_secret"]
        self.access_token_key = config["access_token_key"]
        self.access_token_secret = config["access_token_secret"]
        self.twitter_handle_list = config["twitter_handle_list"]
        self.twitter_handle_filter_list = config["twitter_handle_filter_list"]

        # Pre defined constants for Twitter
        self.timestamp_key = "created_at"
        self.timestamp_format = "%a %b %d %H:%M:%S %z %Y"
        self.message_key = "text"
        self.timezone = "GMT"

class SpreadSheetReviewChannel(ReviewChannel):
    """ The configurations specific to Google Spreadsheets.

    Attributes:
        spreadsheet_id: The spreadsheet id.
        sheet_id: The sheet id.
        client_secrets_file: Path to the client-secrets file, generated through the google sheets api.
    """

    def __init__(self, config):
        super().__init__(config)
        self.spreadsheet_id = config["spreadsheet_id"]
        self.sheet_id = config["sheet_id"]
        self.client_secrets_file = config["client_secrets_file"]

class SalesforceReviewChannel(ReviewChannel):
    """ The configurations specific to Salesforce.

    Attributes:
        base_url: The base url of the salesforce api.
        oauth_params: The oauth params required for salesforce.
        query_list: The list of qieroes that you want to execute.
    """

    def __init__(self, config):
        super().__init__(config)
        self.base_url = config["base_url"]
        self.oauth_params = config["oauth_params"]
        self.query_list = config["query_list"]

class FawkesInternalDataConfig:
    """ The configurations specific to internals of where fawkes stores the intermediate data files.

    Attributes:
        base_folder: The base folder path to store all the files.
        raw_data_folder: The folder path to store all the raw data.
        parsed_data_folder: The folder path to store all the parsed files.
        processed_data_folder: The folder path to store all the processed files.
        models_folder: The folder path to store all the machine learning models.
        emails_folder: The folder path to store all the generted emails.
    """

    def __init__(self, config):
        self.base_folder = config["base_folder"]
        self.raw_data_folder = config["raw_data_folder"]
        self.parsed_data_folder = config["parsed_data_folder"]
        self.processed_data_folder = config["processed_data_folder"]
        self.models_folder = config["models_folder"]
        self.emails_folder = config["emails_folder"]
        self.query_response_folder = config["query_response_folder"]

class FawkesInternalConfig:
    """ The internal configurations of fawkes exposed so that users can modify as required.

    Attributes:
        data: Configuration options related to data.
    """

    def __init__(self, config):
        self.data = FawkesInternalDataConfig(config["data"])

class AppConfig:
    """ The configuration for running Fawkes for a particular app.


Definition of a Review Channel.

    Attributes:
        app: The application level properties.
        elastic_config: The configurations required for ElasticSearch and Kibana.
        email_config: The configurations required for sending an email summary from fawkes.
        slack_config: The configurations required for sending user reviews to slack and triggering custom notifications.
        jira_config: The configurations required to add Jira related information in the slack notification.
        algorithm_config: The configurations required for running algorithms.
        env_keys: A list of variables in the configs which need to fetched from the environment variables of the system.
        custom_code_module_path: The file to any custom code that need to be executed at different stages.
        fawkes_internal_config: The internal configurations of fawkes exposed so that users can modify as required.
        review_channels: A list of review channel configuration.
    """

    def __init__(self, config):
        # First we convert any env-keys to their actual values.
        config = self.inject_env_vars_as_values(config)
        # Validate config with schema
        self.validate_app_config_schema(config)
        # We initialize each of the attributes of AppConfig
        self.app = App(config["app"])
        self.elastic_config = ElasticConfig(config["elastic_config"])
        self.email_config = EmailConfig(config["email_config"])
        self.slack_config = SlackConfig(config["slack_config"])
        self.jira_config = JiraConfig(config["jira_config"])
        self.algorithm_config = AlgorithmConfig(config["algorithm_config"])
        self.env_keys = config["env_keys"]
        self.custom_code_module_path = config["custom_code_module_path"]
        self.fawkes_internal_config = FawkesInternalConfig(config["fawkes_internal_config"])

        # Add the review channels
        self.review_channels = []

        # Determine the channel_type and initialize the object accordingly
        for review_channel in config["review_channels"]:
            if review_channel["channel_type"] == ReviewChannelTypes.IOS:
                self.review_channels.append(
                    AppStoreReviewChannel(review_channel)
                )
            elif review_channel["channel_type"] == ReviewChannelTypes.ANDROID:
                self.review_channels.append(
                    PlayStoreReviewChannel(review_channel)
                )
            elif review_channel["channel_type"] == ReviewChannelTypes.TWITTER:
                self.review_channels.append(
                    TwitterReviewChannel(review_channel)
                )
            elif review_channel["channel_type"] == ReviewChannelTypes.SPREADSHEET:
                self.review_channels.append(
                    SpreadSheetReviewChannel(review_channel)
                )
            else:
                self.review_channels.append(
                    ReviewChannel(review_channel)
                )

    def inject_env_vars_as_values(self, config):
        config_string = json.dumps(config)
        env_vars = config["env_keys"]

        for key in env_vars:
            config_string = config_string.replace(
                key,
                os.environ[key]
            )
        return json.loads(config_string)

    def validate_app_config_schema(self, document):
        try:
            schema = utils.open_json(
                constants.APP_CONFIG_SCHEMA_FILE
            )
            jsonschema.validate(document, schema)
        except ValidationError as e:
            raise ValidationError("App config schema validation failed: " + str(e.message))
