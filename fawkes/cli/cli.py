""" This will serve as the CLI for fawkes """
import argparse
import sys
import os

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import fawkes.constants.constants as constants

import fawkes.fetch.fetch as fetch
import fawkes.parse.parse as parse
import fawkes.algorithms.algo as algo
import fawkes.email_summary.email_summary_detailed as email_summary_detailed
import fawkes.email_summary.send_email as send_email
import fawkes.datastore.elasticsearch as elasticsearch
import fawkes.slackbot.slackbot as slackbot
import fawkes.algorithms.categorisation.text_match.trainer as text_match_trainer
import fawkes.algorithms.categorisation.lstm.trainer as lstm_trainer

class FawkesActions:
    FETCH = 'fetch'
    PARSE = 'parse'
    RUN_ALGO = 'run.algo'
    GENERATE_EMAIL = 'email.generate'
    SEND_EMAIL = 'email.send'
    PUSH_ELASTICSEARCH = 'push.elasticsearch'
    QUERY_ELASTICSEARCH = 'query.elasticsearch'
    PUSH_SLACK = 'push.slack'
    GENERATE_TEXT_MATCH_KEYWORDS = 'generate.text_match.keywords'
    TRAIN_LSTM_MODEL = 'train.model.lstm_classification'

def define_arguments(parser):
    # Specify an action
    parser.add_argument(
        "action",
        help="The action that's supposed to be done.",
        type=str,
        choices=[
            FawkesActions.FETCH,
            FawkesActions.PARSE,
            FawkesActions.RUN_ALGO,
            FawkesActions.GENERATE_EMAIL,
            FawkesActions.SEND_EMAIL,
            FawkesActions.PUSH_ELASTICSEARCH,
            FawkesActions.QUERY_ELASTICSEARCH,
            FawkesActions.PUSH_SLACK,
            FawkesActions.GENERATE_TEXT_MATCH_KEYWORDS,
            FawkesActions.TRAIN_LSTM_MODEL,
        ],
    )
    # Specify app-configs file path
    parser.add_argument(
        "-c", "--config",
        help="The path to the app-config.json file.",
        type=str,
        default=constants.FAWKES_CONFIG_FILE,
    )
    # Specify query index for elasticsearch query
    parser.add_argument(
        "-q", "--query",
        help="The query index for elasticsearch query",
        type=str,
        default="",
    )
    # Specify response file format for elasticsearch query
    parser.add_argument(
        "-f", "--format",
        help="The response file format for elasticSearch query",
        type=str,
        default=constants.JSON,
    )

if __name__ == "__main__":
    # Init the arg parser
    parser = argparse.ArgumentParser()
    # Defining all the arguments
    define_arguments(parser)
    # Extracting all the arguments
    args = parser.parse_args()

    # Depending on the args, we execute the commands.
    action = args.action
    app_config_file = args.config
    query_term = args.query
    query_response_file_format = args.format

    if action == FawkesActions.FETCH:
        fetch.fetch_reviews(app_config_file)
    elif action == FawkesActions.PARSE:
        parse.parse_reviews(app_config_file)
    elif action == FawkesActions.RUN_ALGO:
        algo.run_algo(app_config_file)
    elif action == FawkesActions.GENERATE_EMAIL:
        email_summary_detailed.generate_email_summary_detailed(app_config_file)
    elif action == FawkesActions.SEND_EMAIL:
        send_email.send_email(app_config_file)
    elif action == FawkesActions.PUSH_ELASTICSEARCH:
        elasticsearch.push_data_to_elasticsearch(app_config_file)
    elif action == FawkesActions.QUERY_ELASTICSEARCH:
        elasticsearch.query_from_elasticsearch(app_config_file, query_term = query_term, format = query_response_file_format)
    elif action == FawkesActions.PUSH_SLACK:
        slackbot.send_reviews_to_slack(app_config_file)
    elif action == FawkesActions.GENERATE_TEXT_MATCH_KEYWORDS:
        text_match_trainer.generate_keyword_weights(app_config_file)
    elif action == FawkesActions.TRAIN_LSTM_MODEL:
        lstm_trainer.train_lstm_model(app_config_file)
    else:
        raise Exception("Invalid action!")

