import os
import sys
from datetime import datetime

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import src.utils as utils
from src.config import *


def numberOfReview(reviews):
    return len(reviews)


def topCategory(reviews):
    if len(reviews) > 1:
        return utils.most_common([
            review[DERIVED_INSIGHTS][CATEGORY]
            for review in reviews
            if review[DERIVED_INSIGHTS][CATEGORY] != CATEGORY_NOT_FOUND
        ])
    else:
        return reviews[0][DERIVED_INSIGHTS][CATEGORY]


def numFeatureReq(reviews):
    return len([
        review for review in reviews
        if review[DERIVED_INSIGHTS][EXTRA_PROPERTIES][BUG_FEATURE] == FEATURE
    ])


def numBugsReported(reviews):
    return len([
        review for review in reviews
        if review[DERIVED_INSIGHTS][EXTRA_PROPERTIES][BUG_FEATURE] == BUG
    ])


def appStoreRating(reviews):
    reviews = [
        review for review in reviews
        if review[CHANNEL_TYPE] == CHANNEL_NAME_APPSTORE
    ]
    if len(reviews) == 0:
        return 0.0
    l = [review[PROPERTIES][RATING] for review in reviews]
    return float(sum(l)) / len(l)


def playStoreRating(reviews):
    reviews = [
        review for review in reviews
        if review[CHANNEL_TYPE] == CHANNEL_NAME_PLAYSTORE
    ]
    if len(reviews) == 0:
        return 0.0
    l = [review[PROPERTIES][RATING] for review in reviews]
    return sum(l) / len(l)


def happyReview1(reviews):
    return sorted(reviews, key=utils.get_sentiment_compound,
                  reverse=True)[0][MESSAGE]


def unhappyReview1(reviews):
    return sorted(reviews, key=utils.get_sentiment_compound)[0][MESSAGE]


def positiveReview(reviews):
    return len([
        review for review in reviews
        if utils.get_sentiment_compound(review) > 0.0
    ])


def neutralReview(reviews):
    return len([
        review for review in reviews
        if utils.get_sentiment_compound(review) == 0.0
    ])


def negativeReview(reviews):
    return len([
        review for review in reviews
        if utils.get_sentiment_compound(review) < 0.0
    ])


def topCategoryNumberOfReview(reviews):
    tc = topCategory(reviews)
    return len([
        review for review in reviews if review[DERIVED_INSIGHTS][CATEGORY] == tc
    ])


def fromDate(reviews):
    return min([
        datetime.strptime(review[TIMESTAMP], '%Y/%m/%d %H:%M:%S')
        for review in reviews
    ]).strftime('%b %d')


def toDate(reviews):
    return max([
        datetime.strptime(review[TIMESTAMP], '%Y/%m/%d %H:%M:%S')
        for review in reviews
    ]).strftime('%b %d')


def getVocByCategory(reviews):
    review_by_cat = {}
    for review in reviews:
        if review[DERIVED_INSIGHTS][CATEGORY] in review_by_cat:
            review_by_cat[review[DERIVED_INSIGHTS][CATEGORY]].append(review)
        else:
            review_by_cat[review[DERIVED_INSIGHTS][CATEGORY]] = [review]
    return review_by_cat


def playStoreNumberReview(reviews):
    reviews = [
        review for review in reviews
        if review[CHANNEL_TYPE] == CHANNEL_NAME_PLAYSTORE
    ]
    return len(reviews)


def appStoreNumberReview(reviews):
    reviews = [
        review for review in reviews
        if review[CHANNEL_TYPE] == CHANNEL_NAME_APPSTORE
    ]
    return len(reviews)
