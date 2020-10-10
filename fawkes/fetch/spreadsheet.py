import os
import sys

from gsheets import Sheets

# This is so that below import works
sys.path.append(os.path.realpath("."))

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

def fetch_sheet_data(token_file, spreadsheet_id):
    """
     We fetch the google sheets given spreadsheet id and sheet id and then dump it into csv
     https://docs.google.com/spreadsheets/d/spreadsheetId/edit#gid=sheet_id

     Enable google drive API and Google Sheets API in google developer console. Check these APIs in OAuth consent screen
    """
    sheets_object = Sheets.from_files(token_file, "storages.json")
    sheets = sheets_object[spreadsheet_id]
    return sheets


def fetch(review_channel):
    sheets = fetch_sheet_data(review_channel.client_secrets_file, review_channel.spreadsheet_id)
    # Funny enough, there is no direct way to put into a csv string.
    return sheets[review_channel.sheet_id].to_frame().to_csv()
