import json
import os
from pprint import pprint

class App:
    def __init__(self, config):
        self.name = config["name"]
        self.logo = config["logo"]

class ElasticConfig:
    def __init__(self, config):
        self.index = config["index"]
        self.elastic_search_url = config["elastic_search_url"]
        self.kibana_url = config["kibana_url"]
        self.lifetime_rating_index = config["lifetime_rating_index"]

class EmailConfig:
    def __init__(self, config):
        self.email_template_file = config["email_template_file"]
        self.email_time_span = config["email_time_span"]
        self.email_time_span_in_words = config["email_time_span_in_words"]
        self.email_subject_name = config["email_subject_name"]
        self.sender_email_address = config["sender_email_address"]
        self.email_list = config["email_list"]
        self.sendgrid_api_key = config["sendgrid_api_key"]

class SlackCustomNotifications:
    def __init__(self, config):
        self.category_based_rules = config["category_based_rules"]
        self.keyword_based_rules = config["keyword_based_rules"]

class SlackConfig:
    def __init__(self, config):
        self.slack_channel = config["slack_channel"]
        self.slack_hook_url = config["slack_hook_url"]
        self.slack_run_interval = config["slack_run_interval"]
        self.slack_notification_rules = SlackCustomNotifications(config["slack_notification_rules"])

class JiraConfig:
    def __init__(self, config):
        self.base_url = config["base_url"]
        self.project_id = config["project_id"]
        self.story_type = config["story_type"]
        self.bug_type = config["bug_type"]

class CategorizationAlgorithms:
    TEXT_MATCH_CLASSIFICATION = "text_match"
    LSTM_CLASSIFICATION = "lstm_classification"

class AlgorithmConfig:
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

class ReviewChannel:
    def __init__(self, config):
        self.channel_type = config["channel_type"]
        self.channel_name = config["channel_name"]
        self.file_type = config["file_type"]
        self.file_path = config["file_path"]
        self.is_channel_enabled = config["is_channel_enabled"]
        self.weekly_summary = config["weekly_summary"]
        self.timestamp_key = config["timestamp_key"]
        self.timestamp_format = config["timestamp_format"]
        self.timezone = config["timezone"]
        self.message_key = config["message_key"]
        self.rating_key = config["rating_key"]

class AppStoreReviewChannel(ReviewChannel):
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
    def __init__(self, config):
        super().__init__(config)
        self.app_id = config["app_id"]
        self.searchman_api_key = config["searchman_api_key"]

        # Pre defined constants for Play. Store.
        self.timestamp_key = "timestamp"
        self.message_key = "content"

class TwitterReviewChannel(ReviewChannel):
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
    def __init__(self, config):
        super().__init__(config)
        self.spreadsheet_id = config["spreadsheet_id"]
        self.sheet_id = config["sheet_id"]
        self.client_secrets_file = config["client_secrets_file"]

class SalesforceReviewChannel(ReviewChannel):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config["base_url"]
        self.oauth_params = config["oauth_params"]
        self.query_list = config["query_list"]

class FawkesInternalDataConfig:
    def __init__(self, config):
        self.base_folder = config["base_folder"]
        self.raw_data_folder = config["raw_data_folder"]
        self.parsed_data_folder = config["parsed_data_folder"]
        self.processed_data_folder = config["processed_data_folder"]
        self.models_folder = config["models_folder"]
        self.emails_folder = config["emails_folder"]

class FawkesInternalConfig:
    def __init__(self, config):
        self.data = FawkesInternalDataConfig(config["data"])

class AppConfig:
    def __init__(self, config):
        # First we convert any env-keys to their actual values.
        config = self.inject_env_vars_as_values(config)
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

