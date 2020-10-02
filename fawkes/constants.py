# Fields in unified json
TIMESTAMP = "timestamp"
MESSAGE = "message"
CHANNEL_TYPE = "channel_type"
PROPERTIES = "properties"
APP = "app"
DERIVED_INSIGHTS = "derived_insight"
EXTRA_PROPERTIES = "extra_properties"
CATEGORY_SCORES = "category_scores"
CATEGORY = "category"
SENTIMENT = "sentiment"
COMPOUND = "compound"
TIMEZONE = "timezone"
RAW_REVIEW = "raw_review"

# String constants
TWITTER_QUERY_LANGUAGE = "en"
KEY_CONTAINING_TWEETS = "statuses"
TIMESTAMP_KEY = "timestamp-key"
MESSAGE_KEY = "message-key"
TWITTER_HANDLE_BALCKLIST = "twitter-handle-blacklist"
KEY_WITH_STATUS_ID = "id"
KEY_WITH_TWEET_URL = "tweet-url"
REVIEW_CHANNELS = "review-channels"
SALESFORCE_ACCESS_TOKEN_KEY = "access_token"
SALESFORCE_QUERY_LIST = "salesforce-query-list"
SALESFORCE_BASE_URL = "salesforce-base-url"
SALESFORCE_PAGINATION_URL = "nextRecordsUrl"
SALESFORCE_OAUTH_PARAMS = "salesforce-oauth-params"
TWITTER_HANDLE_LIST = "twitter-handle-list"
AMPERSAND = "&"
BLANK = "blank"
AT_ENCODED = "%40"
SPREADSHEET_ID = "spreadsheet-id"
SHEET_ID = "sheet-id"
CLIENT_SECRET_FILE = "path-to-client-secrets"
CHANNEL_NAME = "channel-name"
CONSUMER_KEY = "consumer-key"
CONSUMER_SECRET = "consumer-secret"
ACCESS_TOKEN_KEY = "access-token-key"
ACCESS_TOKEN_SECRET = "access-token-secret"
IS_CHANNEL_ENABLED = "is-channel-enabled"
RECORDS = "records"
DONE = "done"
FILE_TYPE = "file-type"
CUSTOM_CODE_PATH = "custom-code-path"
HASH_ID = "hash-id"
FILE_PATH = "file-path"
BUG_FEATURE = "bug_feature"
LSTM_CATEGORY = "lstm_category"
BUG = "bug"
FEATURE = "feature"
APP_ID = "app-id"
SEARCHMAN_API_KEY = "searchman-api-key"
COUNTRY = "country"
ALGORITHM_DAYS_FILTER = "algorithm-days-filter"
CATEGORIZATION_ALGORITHM = "categorization-algorithm"
EMAIL_SUBJECT_NAME = "email-subject-name"
EMAIL_LIST = "email-list"
WEEKLY_SUMMARY = "weekly-summary"
APP_LOGO = "app-logo"
EMAIL_TIME_SPAN_WORDS = "email-time-span"
TOPIC_KEYWORDS_FILE = "topic-keywords-file"
BUG_FEATURE_FILE = "bug-feature-file"
LIFETIME_RATING_ELASTICSEARCH_INDEX = "lifetime-rating-elastic-search-index"
CHANNEL_TYPE_SPREADSHEET = "spreadsheet"
CHANNEL_TYPE_TWITTER = "twitter"
CHANNEL_TYPE_APPSTORE = "ios"
CHANNEL_TYPE_PLAYSTORE = "android"
CHANNEL_TYPE_SALESFORCE = "salesforce"
CHANNEL_TYPE_CSV = "csv"

CHANNEL_NAME_TWITTER = "twitter"
CHANNEL_NAME_PLAYSTORE = "playstore"
CHANNEL_NAME_APPSTORE = "appstore"

JSON = "json"
CSV = "csv"

TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M:%S"

# Salesforce related stuff
SALESFORCE_EXTRACTION_DAYS = 10

# PARSING MODULE
# All about care transcripts
CONVERSATION_START_STRING = "Website visitor has joined the conversation"
CONVERSATION_END_STRING = "Website visitor has left the conversation"
PERSON_TIME_STAMP_REGEX = r"[\t|\s]*([\d+:]*\d+[\s]*(?:AM|PM))"

# in-app
PLATFORM_ANDROID = "Android Phone"
RATING = "rating"
FEEDBACK = "feedback"
NA_STRING = "NA"
EMPTY = ""

# Twitter parse relateds
TWITTER_URL = "https://twitter.com/i/web/status/{status_id}"
POSSIBLY_SENSITIVE = "possibly_sensitive"

# App Store
APP_STORE_RSS_URL = "https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/page={page_number}/sortBy=mostRecent/xml"
APP_STORE_APP_URL = "https://apps.apple.com/us/app/id{app_id}"
APPSTORE_CLASS_TYPE = "span"
APPSTORE_CLASS_NAME = "we-customer-ratings__averages__display"
APP_STORE_PAGES_TO_FETCH = 10

# Play Store
PLAY_STORE_APP_URL = "https://play.google.com/store/apps/details?id={app_id}"
PLAYSTORE_CLASS_TYPE = "div"
PLAYSTORE_CLASS_NAME = "BHMmbe"
PLAYSTORE_FETCH_PAGES = 1

# Categorization algorithms
LSTM_CLASSIFICATION = "lstm-classifier"
TEXT_MATCH_CLASSIFIER = "text-match-classifier"

# File paths
DATA_DUMP_DIR = "data/"
APP_CONFIG_FILE = "app/{file_name}"
APP_CONFIG_FILE_NAME = "app-config.json"
PROCESSED_DATA_DIR = "processed-data/"
PARSED_INTEGRATED_REVIEW_FILE = "processed-data/{app_name}-parsed-integrated-review.json"
PROCESSED_INTEGRATED_REVIEW_FILE = "processed-data/{app_name}-processed-integrated-review.json"
PROCESSED_EMAIL_FILE = "processed-data/{app_name}-processed-email.html"
TOPICS_WEIGHT_FILE = "app/{app}-keywords-with-weight.json"

RAW_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/{channel_name}-raw-feedback.{extension}"
PARSED_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/parsed-user-feedback.json"
PROCESSED_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/processed-user-feedback.json"
LSTM_CATEGORY_MODEL_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-trained-model.h5"
LSTM_CATEGORY_ARTICLE_TOKENIZER_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-article-tokenizer.json"
LSTM_CATEGORY_LABEL_TOKENIZER_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-label-tokenizer.json"
EMAIL_SUMMARY_GENERATED_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/email-summary-generated.html"

BUG_FEATURE_FILE_WITH_WEIGHTS = "app/{app}-bug-feature-file-with-weights.json"
TRAINED_MODELS = "trained-models/"
LSTM_TRAINED_MODEL_FILE = TRAINED_MODELS + "lstm-{app_name}-trained.h5"
LSTM_ARTICLE_TOKENIZER_FILE = TRAINED_MODELS + \
    "lstm-article-tokenizer-{app_name}.json"
LSTM_LABEL_TOKENIZER_FILE = TRAINED_MODELS + \
    "lstm-label-tokenizer-{app_name}.json"

# generic cleanup
URL_REGEX = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=% &:/~+#-]*[\w@?^=%&/~+#-])?"
LINK_REGEX = "<[^>]+>"

LDA_MODEL_SAVE_FILE = "trained-models/all/all-channels-lda-model.lda"
LDA_TOPIC_FILE = "processed-data/intergrated-review-lda-topics-07.json"
LDA_MODEL_CORPUS_SAVE_FILE = "processed-data/corpus-lda"
LDA_MODEL_ID2WORD_SAVE_FILE = "trained-models/all/all-channels-lda-model.lda.state"

GLOVE_WORD_EMBEDDING_READ_FILE = "configs/glove-twitter-word-embedding.txt"

# Summary
SUMMARY_NUM_LINES = 5
POSTIVE_SENTIMENT = "positive"
NEGATIVE_SENTIMENT = "negative"
TWEET_LIMIT = 5

# Elasticsearch related
ELASTIC_SEARCH_URL = "elastic-search-url"
KIBANA_DASHBOARD_URL = "kibana-dashboard-url"
ELASTIC_SEARCH_INDEX_KEY = "elastic-search-index"
BULK_UPLOAD_SIZE = 10000
NEW_LINE = "\n"
SPACE = " "

# Slackbot related
SLACK_CHANNEL_NAME = "slack-channel"
SLACK_HOOK_URL = "slack-hook-url"
SLACKBOT_MINUTES_FILTER = "slackbot-run-interval"
SLACK_TAGS = "slack-tags"
SLACK_KEYWORDS = "keywords"
JIRA_ISSUE_URL_TEMPLATE = "{base_url}/secure/CreateIssueDetails!init.jspa?{params}"
JIRA = "jira"
PROJECT_ID = "project-id"
STORY_ISSUE_TYPE = "story-issue-type"
BUG_ISSSUE_TYPE = "bug-issue-type"
JIRA_BASE_URL = "base-url"

# Searchman
SEARCHMAN_REVIEWS_ENDPOINT = "http://api.searchman.io/v1/{platform}/us/app/reviews"

# text-match related
CATEGORY_NOT_FOUND = "uncategorized"

# Categorized docs
CARE_TRANSCRIPTS_CATEGORIZED_SIMPLE_TEXT = "data-parsed/care/care-transcripts-categorized-simple-text.json"

# Multiprocessing related
PROCESS_NUMBER = 6

# Improvement of keywords
IMPROVEMENT_KEYWORDS_NUMBER = 20
IMPROVED_CATEGORY_KEYWORDS = "app/improved-{app_name}-category-keywords.json"
CIRCLECI = "CIRCLECI"

# Email notification service
SENDER_EMAIL_ADDRESS = "sender-email-address"
WEEKLY_EMAIL_TEMPLATE = "fawkes/email_summary/templates/weekly.html"
WEEKLY_EMAIL_DETAILED_TEMPLATE = "fawkes/email_summary/templates/weekly-detailed.html"
WEEKLY_EMAIL_DETAILED_REVIEW_BLOCK_TEMPLATE = "fawkes/email_summary/templates/weekly-detailed-review-block.html"
SENDGRID_API_KEY = "sendgrid-api-key"

# environment variables list
ENV_KEYS = "env-keys"
