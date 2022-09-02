import os
import json
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb_client = boto3.client("dynamodb")


def get_item_from_dynamodb(blob_id: str):
    """
    Receives blob id in order to search and return data of dynamodb item.

    :param blob_id:
        Id to get access to dynamodb item.
    :return: Item data.
    """
    try:
        item = dynamodb_client.get_item(
            TableName=TABLE_NAME,
            Key={
                "blob_id": {
                    "S": blob_id
                }
            }).get("Item")
    except:
        return None

    return item


def get_blob_info(event, context):
    blob_id = event["pathParameters"]["blob_id"]

    item = get_item_from_dynamodb(blob_id)

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "record about received blob id is not found"})
        }

    try:
        response = {
            "blob_id": item["blob_id"]["S"],
            "labels": item["labels"]["L"]
        }
    except:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "image was not loaded yet"})
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
