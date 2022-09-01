#!/usr/bin/env python3

import aws_cdk as cdk

from aws_recognition_labels_cdk.aws_recognition_labels_cdk_stack import AwsRecognitionLabelsCdkStack


app = cdk.App()
AwsRecognitionLabelsCdkStack(app, "aws-recognition-labels-cdk")

app.synth()
