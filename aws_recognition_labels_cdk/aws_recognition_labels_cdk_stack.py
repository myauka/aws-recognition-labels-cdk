from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_lambda_event_sources as l_trigger,
    aws_lambda as aws_lambda,
    aws_dynamodb as ddb,
    aws_s3_notifications
)


class AwsRecognitionLabelsCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # definition of services
        bucket = s3.Bucket(self, 'cdk-rekognition-labels-myauka-blobs-bucket')

        table = ddb.Table(
            self, 'cdk-rekognition-labels-myauka-results-table',
            partition_key=ddb.Attribute(name='blob_id', type=ddb.AttributeType.STRING)
        )

        # functions
        put_blob_lambda = aws_lambda.Function(
            self, 'put_blob',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset('handlers'),
            handler='put_blob.put_blob',
            environment=dict(
                TABLE_NAME=table.table_name,
                BUCKET_NAME=bucket.bucket_name
            )
        )

        get_blob_lambda = aws_lambda.Function(
            self, 'get_blob_info',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset('handlers'),
            handler='get_blob_info.get_blob_info',
            environment=dict(
                TABLE_NAME=table.table_name,
                BUCKET_NAME=bucket.bucket_name
            )
        )

        search_labels_lambda = aws_lambda.Function(
            self, 'get_blob_info',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset('handlers'),
            handler='search_labels.process_blob',
            environment=dict(
                TABLE_NAME=table.table_name,
                BUCKET_NAME=bucket.bucket_name
            )
        )
        search_labels_lambda.add_event_source(
            l_trigger.S3EventSource(
                bucket,
                events=[s3.EventType.OBJECT_CREATED]
            )
        )

        make_callback_lambda = aws_lambda.Function(
            self, 'make_callback',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset('handlers'),
            handler='make_callback.make_callback',
            environment=dict(
                TABLE_NAME=table.table_name,
            )
        )
        make_callback_lambda.add_event_source(
            l_trigger.DynamoEventSource(
                table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=1,
            )
        )

        # iam
        statement = iam.PolicyStatement()
        statement.add_actions(
            "rekognition:*",
            "dynamodb:*",
            "s3:*"
        )
        statement.add_resources("*")

        put_blob_lambda.add_to_role_policy(statement)
        get_blob_lambda.add_to_role_policy(statement)
        search_labels_lambda.add_to_role_policy(statement)
        make_callback_lambda.add_to_role_policy(statement)

        # api gateway
        service_api = apigateway.RestApi(self, 'cdk-reko-api', rest_api_name='cdk-reko-api')
        blobs_post_api = service_api.root.add_resource('blobs')
        tmp = apigateway.LambdaIntegration(put_blob_lambda)
        blobs_post_api.add_method('POST', tmp)

        blob_get_api = service_api.root.add_resource('blob/{blob_id}')
        tmp2 = apigateway.LambdaIntegration(get_blob_lambda)
        blob_get_api.add_method('GET', tmp2)

        # api_with_methods = apigateway.RestApi(self, id='cdk-api-gateway-rekognition-labels')
        # put_blob_api = api_with_methods.add_method('POST')
        # get_blob = api_with_methods.
        # search_labels
        # make_callback

        # notification = aws_s3_notifications.LambdaDestination(search_labels_lambda)

        # base_lambda.function_name

        # bucket = s3.Bucket(self, "aws-rekognition-labels-cdk-myauka-blobs-bucket")
