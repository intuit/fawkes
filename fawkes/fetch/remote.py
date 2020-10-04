import urllib.request

def fetch(review_channel):
    return urllib.request.urlopen(review_channel.file_path).read().decode("utf-8")
