import os
import json
import uuid
import boto3
import re

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3_client = boto3.client("s3")
dynamodb_client = boto3.client("dynamodb")


def validator(url: str):
    """
    Validate urls.

    :param url:
        Just string url.
    :return:
        Result of validation.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url)


def get_callback_url(event: dict):
    """
    Gets callback url from event.

    :param event:
        JSON-formatted document that contains data for a Lambda function to process.
    :return:
        Callback url.
    """
    callback_url = json.loads(event["body"]).get("callback_url")

    if validator(callback_url):
        return callback_url


def make_record_to_dynamodb(randomized_id: str, callback_url: str) -> None:
    """
    Creates and puts item to dynamodb table.

    :param randomized_id:
        Random generated id, which can be used to access the data.
    :param callback_url:
        We will use this url to send a post method with extracted labels later.

    :return: None.
    """
    dynamodb_client.put_item(
        TableName=TABLE_NAME,
        Item={
            "blob_id": {"S": randomized_id},
            "callback_url": {"S": callback_url},
        }
    )


def get_upload_url(randomized_id: str) -> str:
    """
    Generates presigned url, which can be used for uploading image to s3 without full access to s3 bucket.

    :param randomized_id:
        Random generated id, which can be used to access the file from s3 bucket.
    :return:
        Generated presign url.
    """
    upload_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": randomized_id
        },
        ExpiresIn=300
    )
    return upload_url


def put_blob(event, context):
    callback_url = get_callback_url(event)

    if not callback_url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "callback url was not received"})
        }

    randomized_id = str(uuid.uuid4())

    make_record_to_dynamodb(randomized_id, callback_url)

    upload_url = get_upload_url(randomized_id)

    return {
        "statusCode": 201,
        "body": json.dumps({
            "blob_id": randomized_id,
            "callback_url": callback_url,
            "upload_url": upload_url
        })
    }
