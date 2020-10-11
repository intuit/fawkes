import nltk

from pprint import pprint

nltk.download("vader_lexicon", quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()


def get_sentiment(sentence):
    """
    Takes a sentence and returns its sentiment.
    Output format :
    {
        "compound": 0.7906,
        "neg": 0.0,
        "neu": 0.667,
        "pos": 0.333,
    }
    """
    return sid.polarity_scores(sentence)
