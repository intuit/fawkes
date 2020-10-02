import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.realpath("."))

import fawkes.algorithms.lstm_classifier.lstm_classifier as lstm_classifier


class LstmClassifierTest(unittest.TestCase):
    def test_get_articles_and_labels(self):
        review = [
            {
                "message": "I just heard about this budgeting app and I gave it a try and done.",
                "derived-insight": {"category": "sign-in/sign-up"},
            },
            {"message": "", "derived-insight": {"category": "Application"}},
        ]
        result = lstm_classifier.get_articles_and_labels(review)

        cleaned_articles = result[0]
        cleaned_labels = result[1]
        cleaned_labels = result[2]

        # Check if the review message has been cleaned
        self.assertEqual(cleaned_articles[0], "I heard budgeting app I gave try done.")

        # Check if empty articles are removed
        self.assertEqual(len(cleaned_articles), 1)

        # Check if the lengths of cleaned_articles, cleaned_labels and cleaned_labels match
        self.assertEqual(len(cleaned_articles), len(cleaned_labels))
        self.assertEqual(len(cleaned_articles), len(cleaned_labels))

        # Check if non-alphanumeric labels are cleaned
        self.assertEqual(cleaned_labels[0], "signinsignup")

        # Check the original to clean label mapping correctness
        self.assertEqual(
            (cleaned_labels[cleaned_labels[0]]),
            review[0]["derived-insight"]["category"],
        )

    def test_split_data(self):
        articles = ["Article-1", "Article-2", "Article-3", "Article-4", "Article-5"]
        labels = ["Label-1", "Label-2", "Label-3", "Label-4", "Label-5"]
        result = lstm_classifier.split_data(articles, labels)

        # Check if the first 4 articles are a part of training data (0.8)
        self.assertEqual(
            len(result[0]), lstm_classifier.TRAINING_PORTION * len(articles)
        )

        # Check if training + validation data length will add up to articles length
        self.assertEqual((len(result[0]) + len(result[2])), len(articles))

    def test_train(self):

        # Stubbing split_data method
        lstm_classifier.split_data = MagicMock()
        lstm_classifier.split_data.return_value = (
            ["Article1", "Article2", "Article3", "Article4"],
            ["Label1", "Label2", "Label3", "Label4"],
            ["Article5"],
            ["Label5"],
        )

        result = lstm_classifier.train(
            ["Article1", "Article2", "Article3", "Article4", "Article5"],
            ["Label1", "Label2", "Label3", "Label4", "Label5"],
        )

        # Check if the result contains all three model, article_tokenizer and label_tokenizer
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
