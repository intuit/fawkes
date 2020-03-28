import unittest
import sys
import os

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import src.algorithms.algo as algo
import src.parse.parse as parse
import src.utils as utils


class FawkesSanityTest(unittest.TestCase):
    def test_sanity(self):
        """
        Test for sanity that parsing and algorithms are working
        """
        # First we parse the sample data.
        parse.parse_reviews()
        parsed_output = utils.open_json(
            "processed-data/sample-mint-parsed-integrated-review.json"
        )
        expected_parsed_output = [
            {
                "app": "sample-mint",
                "timestamp": "2020/03/15 14:13:17",
                "message": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still cant add all of my financial institutions so my budget is kind of skewed. But other that I can say Im more aware of my spending",
                "channel-type": "appstore",
                "properties": {
                    "updated": "2020-03-15 14:13:17",
                    "rating": 5,
                    "version": "7.1.0",
                    "content": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still can\u00e2\u20ac\u2122t add all of my financial institutions so my budget is kind of skewed. But other that I can say I\u00e2\u20ac\u2122m more aware of my spending",
                },
                "hash-id": "bd488c4c04431bdd8fb7ddb5dcf84d7a8b0479e2",
            }
        ]
        self.assertEqual(parsed_output, expected_parsed_output)

        # We run the algorithms on that data
        algo.run_algo()
        processed_output = utils.open_json(
            "processed-data/sample-mint-processed-integrated-review.json"
        )
        expected_processed_output = [
            {
                "app": "sample-mint",
                "timestamp": "2020/03/15 14:13:17",
                "message": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still cant add all of my financial institutions so my budget is kind of skewed. But other that I can say Im more aware of my spending",
                "channel-type": "appstore",
                "properties": {
                    "updated": "2020-03-15 14:13:17",
                    "rating": 5,
                    "version": "7.1.0",
                    "content": "I just heard about this budgeting app. So I gave it a try. I am impressed thus far. However I still can\u00e2\u20ac\u2122t add all of my financial institutions so my budget is kind of skewed. But other that I can say I\u00e2\u20ac\u2122m more aware of my spending",
                },
                "hash-id": "bd488c4c04431bdd8fb7ddb5dcf84d7a8b0479e2",
                "derived-insight": {
                    "sentiment": {
                        "neg": 0.0,
                        "neu": 0.928,
                        "pos": 0.072,
                        "compound": 0.4767,
                    },
                    "extra-properties": {
                        "category-scores": {
                            "User Experience": 0,
                            "sign-in/sign-up": 0,
                            "Notification": 0,
                            "Application": 1,
                            "ads": 0,
                        },
                        "bug-feature": "feature",
                    },
                    "category": "Application",
                },
            }
        ]
        self.assertEqual(processed_output, expected_processed_output)


if __name__ == "__main__":
    unittest.main()
