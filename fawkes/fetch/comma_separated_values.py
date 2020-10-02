from shutil import copyfile
import fawkes.utils.utils as utils
import fawkes.constants as constants

def fetch_csv(review_channel):
    """ Reads a CSV file and returns the string """
    with open (review_channel.file_name) as file:
        return file.read()
    return ""
