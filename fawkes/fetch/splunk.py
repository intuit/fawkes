import json
import splunklib.client as client
import splunklib.results as results


def fetch(review_channel):
    reviews = []
    try:
        service = client.connect(
            host=review_channel.host,
            port=review_channel.port,
            username=review_channel.username,
            password=review_channel.password,
            scheme="https",
            basic=True,
        )

        query = "search {}".format(review_channel.query)
        stream = service.jobs.export(query)

        reader = results.ResultsReader(stream)
        for result in reader:
            if isinstance(result, dict):
                review = json.loads(result["_raw"])
                reviews.append(review)

    except BaseException:
        print("Error while querying data from Splunk")

    return reviews
