# Modular composable utility functions to filter user reviews for different purposes.
# There are many usecases where different filters apply.
# Fetch, Parse, Algorithms, Slackbot, Email Summary, Elastic Search

# Given a set of review_channels, filters out review channels which are disabled
def filter_disabled_review_channels(app_config):
    return [
        review_channel.channel_name for review_channel in app_config.review_channels if review_channel.is_channel_enabled == True
    ]

# Given a set of reviews and review channels, filters out the reviews which have a different review channel than the one in the list.
def filter_reviews_by_channel(reviews, review_channels):
    return [
        review for review in reviews if review.channel_name in review_channels
    ]

# Given a set of reviews and a earliest date-time, filters our reviews which are before the time
def filter_reviews_by_time(reviews, earliest_date_time):
    return [
        review for review in reviews if review.timestamp > earliest_date_time
    ]
