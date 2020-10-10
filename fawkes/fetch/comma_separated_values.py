from shutil import copyfile

import fawkes.utils.utils as utils
import fawkes.constants.constants as constants

def fetch(review_channel):
    """ Reads a CSV file and returns the string """
    with open (review_channel.file_name) as file:
        return file.read()
    return ""
