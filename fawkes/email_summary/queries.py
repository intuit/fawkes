import os
import sys
from datetime import datetime

# this is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants
from fawkes.configs.app_config import ReviewChannelTypes

def numberOfReview(reviews):
    return len(reviews)


def topCategory(reviews):
    if len(reviews) > 1:
        return utils.most_common([
            review.derived_insight.category
            for review in reviews
            if review.derived_insight.category != constants.CATEGORY_NOT_FOUND
        ])
    else:
        return reviews[0].category


def numFeatureReq(reviews):
    return len([
        review for review in reviews
        if review.derived_insight.extra_properties[constants.BUG_FEATURE] == constants.FEATURE
    ])


def numBugsReported(reviews):
    return len([
        review for review in reviews
        if review.derived_insight.extra_properties[constants.BUG_FEATURE] == constants.BUG
    ])


def appStoreRating(reviews):
    reviews = [
        review for review in reviews
        if review.channel_type == ReviewChannelTypes.IOS
    ]
    if len(reviews) == 0:
        return 0.0
    l = [review.rating for review in reviews]
    return float(sum(l)) / len(l)


def playStoreRating(reviews):
    reviews = [
        review for review in reviews
        if review.channel_type == ReviewChannelTypes.ANDROID
    ]
    if len(reviews) == 0:
        return 0.0
    l = [review.rating for review in reviews]
    return sum(l) / len(l)


def happyReview1(reviews):
    return sorted(reviews, key=utils.get_sentiment_compound,
                  reverse=True)[0].message


def unhappyReview1(reviews):
    return sorted(reviews, key=utils.get_sentiment_compound)[0].message


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
        review for review in reviews if review.derived_insight.category == tc
    ])


def fromDate(reviews):
    return min([
        review.timestamp
        for review in reviews
    ]).strftime('%b %d')


def toDate(reviews):
    return max([
        review.timestamp
        for review in reviews
    ]).strftime('%b %d')


def getVocByCategory(reviews):
    review_by_cat = {}
    for review in reviews:
        if review.derived_insight.category in review_by_cat:
            review_by_cat[review.derived_insight.category].append(review)
        else:
            review_by_cat[review.derived_insight.category] = [review]
    return review_by_cat


def playStoreNumberReview(reviews):
    reviews = [
        review for review in reviews
        if review.channel_type == ReviewChannelTypes.ANDROID
    ]
    return len(reviews)


def appStoreNumberReview(reviews):
    reviews = [
        review for review in reviews
        if review.channel_type == ReviewChannelTypes.IOS
    ]
    return len(reviews)
