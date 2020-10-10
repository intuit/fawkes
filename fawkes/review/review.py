import sys
import os
import re
from datetime import datetime, timedelta
from pytz import timezone

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
        category: The category in which the user review falls.
        extra_properties: Any other extra derived insights. Free flowing dict.
    """

    def __init__(self, derived_insight = None):
        """ Initialiser of the derived insight """

        if derived_insight is None:
            self.sentiment = None
            self.category = constants.CATEGORY_NOT_FOUND
            self.extra_properties = {}
        else:
            self.sentiment = derived_insight["sentiment"]
            self.category = derived_insight["category"]
            self.extra_properties = derived_insight["extra_properties"]

    def to_dict(self):
        """ Converts the DerivedInsight class object to a dict """

        return {
            "sentiment": self.sentiment,
            "category": self.category,
            "extra_properties": self.extra_properties,
        }

class Review:
    """ Definition of a user review.

    When initialising a user review, we also standardise the timestamp and cleanup the message.

    Attributes:
        message: The message in the review.
        timestamp: The timestamp when the review was submitted.
        rating: The rating attached to the review. Ideally a numeric value.
        app_name: The name of the app from where the review originated.
        channel_name: The source/channel name from which the review originated.
        channel_type: The source/type from which the review originated.
        hash_id: A unique id for the review. Determined by sha1 of (message + timestamp).
        derived_insight: The derived insights like category, sentiment etc. associated with review.
        raw_review: The raw review without any modifications.
    """

    def __init__(
        self,
        *review,
        message = "",
        timestamp = "",
        app_name = "",
        channel_name = "",
        channel_type = "",
        rating = None,
        review_timezone="UTC",
        timestamp_format=constants.TIMESTAMP_FORMAT,
        hash_id=None,
    ):
        """ Initialiser of a user review """

        self.message = message
        self.timestamp = timestamp
        self.rating = rating
        self.app_name = app_name
        self.channel_name = channel_name
        self.channel_type = channel_type
        # Determine the hash-id.
        # It should almost in all cases never be overridden.
        if hash_id != None:
            self.hash_id = hash_id
        else:
            # Every review hash id which is unique to the message and the timestamp
            self.hash_id = utils.calculate_hash(message + str(timestamp))
        # Derived Insights
        if constants.DERIVED_INSIGHTS in review[0]:
            self.derived_insight = DerivedInsight(review[0][constants.DERIVED_INSIGHTS])
        else:
            self.derived_insight = DerivedInsight()
        # The raw value of the review itself.
        self.raw_review = review[0]

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
        )

    def to_dict(self):
        """ Converts the Review class object to a dict """

        return {
            "message": self.message,
            "timestamp": self.timestamp.strftime(
                constants.TIMESTAMP_FORMAT # Convert it to a standard datetime format
            ),
            "rating": self.rating,
            "app_name": self.app_name,
            "channel_name": self.channel_name,
            "channel_type": self.channel_type,
            "hash_id": self.hash_id,
            "derived_insight": self.derived_insight.to_dict(),
        }
