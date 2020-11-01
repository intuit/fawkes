"""
    Module for calculating similarity of reviews against a query.
    Implemented using: https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
"""
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)

def embed(input_text):
  return model(input_text)

def get_similar_reviews(reviews, query, num_results):
    pass
