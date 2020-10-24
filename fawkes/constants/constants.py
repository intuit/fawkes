# Fields in unified json
APP = "app"
DERIVED_INSIGHTS = "derived_insight"
EXTRA_PROPERTIES = "extra_properties"
CATEGORY_SCORES = "category_scores"
CATEGORY = "category"
SENTIMENT = "sentiment"

# Twitter Related
TWITTER_QUERY_LANGUAGE = "en"
KEY_CONTAINING_TWEETS = "statuses"
KEY_WITH_STATUS_ID = "id"
KEY_WITH_TWEET_URL = "tweet-url"
TWITTER_URL = "https://twitter.com/i/web/status/{status_id}"
POSSIBLY_SENSITIVE = "possibly_sensitive"

# Salesforce related
SALESFORCE_ACCESS_TOKEN_KEY = "access_token"
SALESFORCE_QUERY_LIST = "salesforce-query-list"
SALESFORCE_BASE_URL = "salesforce-base-url"
SALESFORCE_PAGINATION_URL = "nextRecordsUrl"
SALESFORCE_OAUTH_PARAMS = "salesforce-oauth-params"
SALESFORCE_EXTRACTION_DAYS = 10
RECORDS = "records"
DONE = "done"

# General constants
AMPERSAND = "&"
BLANK = "blank"
AT_ENCODED = "%40"
NA_STRING = "NA"
EMPTY = ""
SPACE = " "

# Google Sheets related
SPREADSHEET_ID = "spreadsheet-id"
SHEET_ID = "sheet-id"

# Categorisation
BUG_FEATURE = "bug_feature"
LSTM_CATEGORY = "lstm_category"
BUG = "bug"
FEATURE = "feature"

# File Types
JSON = "json"
CSV = "csv"
JSON_LINES = "json.lines"

TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M:%S"
UNIX_TIMESTAMP = "unix_timestamp"

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

# File paths
FAWKES_CONFIG_FILE = "app/fawkes-config.json"
APP_CONFIG_SCHEMA_FILE = "fawkes/configs/app-config-schema.json"
RAW_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/{channel_name}-raw-feedback.{extension}"
PARSED_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/parsed-user-feedback.json"
PROCESSED_USER_REVIEWS_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/processed-user-feedback.json"
LSTM_CATEGORY_MODEL_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-trained-model.h5"
LSTM_CATEGORY_ARTICLE_TOKENIZER_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-article-tokenizer.json"
LSTM_CATEGORY_LABEL_TOKENIZER_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/lstm-category-label-tokenizer.json"
EMAIL_SUMMARY_GENERATED_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/email-summary-generated.html"

# Generic cleanup
URL_REGEX = r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=% &:/~+#-]*[\w@?^=%&/~+#-])?"
LINK_REGEX = "<[^>]+>"

# Summary
SUMMARY_NUM_LINES = 5
POSTIVE_SENTIMENT = "positive"
NEGATIVE_SENTIMENT = "negative"
TWEET_LIMIT = 5

# Elasticsearch related
BULK_UPLOAD_SIZE = 10000
NEW_LINE = "\n"
ELASTICSEARCH_FETCH_DATA_FILE_PATH = "{base_folder}/{dir_name}/{app_name}/fetch-query-response.{extension}"

# Slackbot related
JIRA_ISSUE_URL_TEMPLATE = "{base_url}/secure/CreateIssueDetails!init.jspa?{params}"
JIRA = "jira"

# Searchman
SEARCHMAN_REVIEWS_ENDPOINT = "http://api.searchman.io/v1/{platform}/us/app/reviews"

# text-match related
CATEGORY_NOT_FOUND = "uncategorized"

# Multiprocessing related
PROCESS_NUMBER = 6

# Improvement of keywords
IMPROVEMENT_KEYWORDS_NUMBER = 20
IMPROVED_CATEGORY_KEYWORDS = "app/improved-{app_name}-category-keywords.json"
CIRCLECI = "CIRCLECI"
SEARCH = "search"

# Email notification service
WEEKLY_EMAIL_TEMPLATE = "fawkes/email_summary/templates/weekly.html"
WEEKLY_EMAIL_DETAILED_TEMPLATE = "fawkes/email_summary/templates/weekly-detailed.html"
WEEKLY_EMAIL_DETAILED_REVIEW_BLOCK_TEMPLATE = "fawkes/email_summary/templates/weekly-detailed-review-block.html"
