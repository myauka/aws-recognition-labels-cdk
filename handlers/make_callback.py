import json
import boto3
import requests


def get_callback_url_from_record(record: dict) -> str:
    """
    Receives dynamodb record and extracts callback url from recently updated item.

    :param record:
        Dynamodb record.
    :return: Callback url.
    """
    item = record["dynamodb"]["NewImage"]
    callback_url = item["callback_url"]["S"]
    return callback_url


def get_labels_from_record(record: dict) -> list:
    """
    Receives dynamodb record and extracts labels from recently updated item.

    :param record:
        Dynamodb record.
    :return: Extracted earlier labels from blob.
    """
    item = record["dynamodb"]["NewImage"]
    labels = item["labels"]
    return labels


def get_blod_id_from_record(record: dict) -> str:
    """
    Receives dynamodb record and extracts blob id from recently updated item.

    :param record:
        Dynamodb record.
    :return: Blob id.
    """
    print(type(record))
    item = record["dynamodb"]["Keys"]
    blob_id = item["blob_id"]["S"]
    return blob_id


def make_callback(event, context):
    response = {}

    for record in event["Records"]:
        if record["eventName"] == "MODIFY":
            response["blob_id"] = get_blod_id_from_record(record)
            response["labels"] = get_labels_from_record(record)
            callback_url = get_callback_url_from_record(record)

            requests.post(callback_url, json=json.dumps(response))

    return {
        "statusCode": 200,
        "body": "Success"
    }
