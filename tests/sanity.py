import unittest
import sys
import os

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import fawkes.algorithms.algo as algo
import fawkes.parse.parse as parse
import fawkes.utils.utils as utils
import fawkes.algorithms.categorisation.text_match.trainer as text_match_trainer

class FawkesSanityTest(unittest.TestCase):
    def test_sanity(self):
        """
        Test for sanity that parsing and algorithms are working
        """
        # First we parse the sample data.
        parse.parse_reviews()
        parsed_output = utils.open_json(
            "data/parsed_data/sample-mint/parsed-user-feedback.json"
        )
        expected_parsed_output = [
            {
                "message": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still cant add all of my financial institutions so my budget is kind of skewed. But other that I can say Im more aware of my spending",
                "timestamp": "2020/03/15 22:06:17",
                "rating": 5.0,
                "user_id": None,
                "app_name": "sample-mint",
                "channel_name": "appstore",
                "channel_type": "ios",
                "hash_id": "a5461e62ee4eccbab92900ba01d49d9ed0642dcc",
                "derived_insight": {
                    "sentiment": None,
                    "category": "uncategorized",
                    "review_message_encoding": None,
                    "extra_properties": {}
                },
                "raw_review": {
                    "updated": "2020-03-15 14:13:17",
                    "rating": 5,
                    "version": "7.1.0",
                    "content": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still can\u00e2\u20ac\u2122t add all of my financial institutions so my budget is kind of skewed. But other that I can say I\u00e2\u20ac\u2122m more aware of my spending"
                }
            }
        ]
        self.assertEqual(parsed_output, expected_parsed_output)
        # Before running the algorithms, we generate the keyword weights.
        text_match_trainer.generate_keyword_weights()

        # We run the algorithms on that data
        algo.run_algo()

        processed_output = utils.open_json(
            "data/processed_data/sample-mint/processed-user-feedback.json"
        )
        expected_processed_output = [
            {
                "message": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still cant add all of my financial institutions so my budget is kind of skewed. But other that I can say Im more aware of my spending",
                "timestamp": "2020/03/15 22:06:17",
                "rating": 5.0,
                "user_id": None,
                "app_name": "sample-mint",
                "channel_name": "appstore",
                "channel_type": "ios",
                "hash_id": "a5461e62ee4eccbab92900ba01d49d9ed0642dcc",
                "derived_insight": {
                    "sentiment": {
                        "neg": 0.0,
                        "neu": 0.928,
                        "pos": 0.072,
                        "compound": 0.4767
                    },
                    "category": "Application",
                    "review_message_encoding": None,
                    "extra_properties": {
                        "category_scores": {
                            "User Experience": 0,
                            "sign-in/sign-up": 0,
                            "Notification": 0,
                            "Application": 1,
                            "ads": 0
                        },
                        "bug_feature": "feature"
                    }
                },
                "raw_review": {
                    "updated": "2020-03-15 14:13:17",
                    "rating": 5,
                    "version": "7.1.0",
                    "content": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still can\u00e2\u20ac\u2122t add all of my financial institutions so my budget is kind of skewed. But other that I can say I\u00e2\u20ac\u2122m more aware of my spending"
                }
            }
        ]
        self.assertEqual(processed_output, expected_processed_output)

if __name__ == "__main__":
    unittest.main()
