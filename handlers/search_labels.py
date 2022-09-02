import os
import json
import boto3
import urllib.parse

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["TABLE_NAME"]

s3_client = boto3.client("s3")
dynamodb_client = boto3.client("dynamodb")
rekognition_client = boto3.client("rekognition", "us-east-1")


def add_labels_to_item(blob_id: str, labels: list) -> None:
    """
    Adds extracted label to dynamdb item.

    :param blob_id:
        Id to get access to dynamodb item.
    :param labels:
        Labels from blob file, which were obtained using aws rekognition service.
    :return: None.
    """
    dynamodb_client.update_item(
        TableName=TABLE_NAME,
        Key={
            "blob_id": {
                "S": blob_id
            }
        },
        UpdateExpression="SET #labels = :extracted_labels",
        ExpressionAttributeNames={
            "#labels": "labels"
        },
        ExpressionAttributeValues={
            ":extracted_labels": {"L": labels}
        })


def prepare_labels_for_dynamodb(labels: list) -> list:
    """
    Formats extracted labels in order to insert them to dynamodb item.

    :param labels:
        Labels from blob file, which were obtained using aws rekognition service.
    :return: List of prepared data for insertion to dynamodb item.
    """
    list_of_labels = []
    for label in labels:
        formatted_label = {
            "M": {
                "label": {"S": label["Name"]},
                "confidence": {"N": str(label["Confidence"])},
                "parents": {"L": [{"S": str(i)} for i in label["Parents"]]}
            }
        }
        list_of_labels.append(formatted_label)
    return list_of_labels


def extract_labels_from_blob(blob_id: str) -> list:
    """
    Gets and returns extracted labels from blob file by using aws rekognition service.

    :param blob_id:
        Id to get blob file from s3 bucket.
    :return: Extracted from blob list of labels.
    """
    rekognition_results = rekognition_client.detect_labels(Image={
        "S3Object": {"Bucket": BUCKET_NAME, "Name": blob_id}
    })
    return rekognition_results["Labels"]


def process_blob(event, context):
    blob_id = event['Records'][0]['s3']['object']['key']

    labels = extract_labels_from_blob(blob_id)

    formatted_labels = prepare_labels_for_dynamodb(labels)

    add_labels_to_item(blob_id, formatted_labels)

    return {
        "statusCode": 200,
        "body": "Success"
    }
