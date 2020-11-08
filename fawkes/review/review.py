import sys
import os
import re
from datetime import datetime, timedelta
from pytz import timezone
from pprint import pprint

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

url_regex = re.compile(constants.URL_REGEX)

class DerivedInsight:
    """ The Derived Insights from a user review.

    Derived insights include attributes like sentiment, category etc. which are obtained by running algorithms on top of the existing user review.

    Attributes:
        sentiment: The sentiment attached to the user review.
        category: The category in which the user review false.
        review_message_encoding: The sentence encoding into a vector.
        extra_properties: Any other extra derived insights. Free flowing dict.
    """

    def __init__(self, derived_insight = None):
        """ Initialiser of the derived insight """

        if derived_insight is None:
            self.sentiment = None
            self.category = constants.CATEGORY_NOT_FOUND
            self.review_message_encoding = None
            self.extra_properties = {}
        else:
            self.sentiment = derived_insight["sentiment"]
            self.category = derived_insight["category"]
            self.review_message_encoding = derived_insight["review_message_encoding"]
            self.extra_properties = derived_insight["extra_properties"]

    def to_dict(self):
        """ Converts the DerivedInsight class object to a dict """

        return {
            "sentiment": self.sentiment,
            "category": self.category,
            "review_message_encoding": self.review_message_encoding,
            "extra_properties": self.extra_properties,
        }

class Review:
    """ Definition of a user review.

    When initialising a user review, we also standardise the timestamp and cleanup the message.

    Attributes:
        message: The message in the review.
        timestamp: The timestamp when the review was submitted.
        rating: The rating attached to the review. Ideally a numeric value..
        user_id: Any identifier which uniquely indetifies a user.
        app_name: The name of the app from where the review originated.
        channel_name: The source/channel name from which the review originated.
        channel_type: The source/type from which the review originated.
        hash_id: A unique id for the review. Determined by sha1 of (message + timestamp).
        derived_insight: The derived insights like category, sentiment etc. associated with review.
        raw_review: The raw review without any modifications.
    """

    def __init__(
        self,
        review,
        *,
        message = "",
        timestamp = "",
        app_name = "",
        channel_name = "",
        channel_type = "",
        rating = None,
        rating_max_value = None,
        user_id = None,
        review_timezone="UTC",
        timestamp_format=constants.TIMESTAMP_FORMAT,
        hash_id=None,
        raw_review = None,
    ):
        """ Initialiser of a user review """

        self.message = message
        self.timestamp = timestamp
        self.app_name = app_name
        self.channel_name = channel_name
        self.channel_type = channel_type

        # Optional but core fields
        # Rating. We check if the rating is present or not.
        if rating != None:
            # Sometimes we get empty strings. So can't assume anything about the data type.
            try:
                self.rating = float(rating)
                # Normalising the rating to be a value between 1 - 5
                if rating_max_value != None:
                    self.rating = constants.RATINGS_NORMALIZATION_CONSTANT * (self.rating / rating_max_value)
            except ValueError:
                self.rating = None
        else:
            self.rating = None
        # User Id.
        self.user_id = user_id

        # Derived Insights
        if constants.DERIVED_INSIGHTS in review:
            self.derived_insight = DerivedInsight(review[constants.DERIVED_INSIGHTS])
        else:
            self.derived_insight = DerivedInsight()

        # The raw value of the review itself.
        # We need to clean it up. https://github.com/intuit/fawkes/issues/58
        self.raw_review = utils.remove_empty_keys(raw_review)

        # Now that we have all info that we wanted for a review.
        # We do some post processing.
        if timestamp_format == constants.UNIX_TIMESTAMP:
            self.timestamp = datetime.fromtimestamp(timestamp)
        else:
            self.timestamp = datetime.strptime(
                timestamp, timestamp_format # Parse it using the given timestamp format
            )

        self.timestamp = self.timestamp.replace(
            tzinfo=timezone(review_timezone) # Replace the timezone with the given timezone
        ).astimezone(
            timezone("UTC") # Convert it to UTC timezone
        )

        # Clean up the message
        # Removes links from message using regex
        self.message = url_regex.sub("", self.message)
        # Removing the non ascii chars
        self.message = (self.message.encode("ascii", "ignore")).decode("utf-8")

        # Determine the hash-id.
        # It should, almost in all cases never be overridden.
        if hash_id != None:
            self.hash_id = hash_id
        else:
            # Every review hash id which is unique to the message and the timestamp
            self.hash_id = utils.calculate_hash(self.message + self.timestamp.strftime(
                constants.TIMESTAMP_FORMAT # Convert it to a standard datetime format
            ) + str(self.user_id))

    @classmethod
    def from_review_json(cls, review):
        """ Initialse a user review object from a dict """

        return cls(
            review,
            message=review["message"],
            timestamp=review["timestamp"],
            app_name=review["app_name"],
            channel_name=review["channel_name"],
            channel_type=review["channel_type"],
            rating=review["rating"],
            user_id=review["user_id"],
            raw_review=review["raw_review"]
        )

    def to_dict(self):
        """ Converts the Review class object to a dict """

        return {
            "message": self.message,
            "timestamp": self.timestamp.strftime(
                constants.TIMESTAMP_FORMAT # Convert it to a standard datetime format
            ),
            "rating": self.rating,
            "user_id": self.user_id,
            "app_name": self.app_name,
            "channel_name": self.channel_name,
            "channel_type": self.channel_type,
            "hash_id": self.hash_id,
            "derived_insight": self.derived_insight.to_dict(),
            "raw_review": self.raw_review,
        }

    def __lt__(self, other):
        return len(self.message) < len(other.message)
