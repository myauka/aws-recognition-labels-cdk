<!--
title: 'AWS Recognition API'
description: 'API for recognition labels on blob files.'
layout: Doc
framework: v3
platform: AWS
language: python
priority: 2
authorLink: 'https://github.com/myauka'
authorName: 'Roman Orlov'
-->


# AWS Recognition API

API for recognition labels on blob files. 

## Usage

API has 2 endpoints:  
POST /blobs - accepts callback_url for receiving callback when recognition will be ended, and return upload_url for uploading pictures.  
GET /blobs/{blob_id} - returns information about recognition results for specified blob.

### For test purposes

In this tutorial I will use UPPERCASE to indicate what **needs to be replaced** or **that you will have other data here.**

**Before testing endpoints**, I highly recommend you to install curl. 
This tool will be used for testing endpoint, but feel free to use any other tool.

After deployment, you will see something like this:
```
✨  Deployment time: 0.0s

Outputs:
aws-recognition-labels-cdk.cdkrekoapiEndpoint = https://id.execute-api.us-east-1.amazonaws.com/prod/
```

You will need this link to test your endpoints out. In app, I defined two endpoints for GET and POST methods. 
Upgrade your link endpoint like this:
```
https://id.execute-api.us-east-1.amazonaws.com/prod/blobs/
```

All right. From now we can send methods to our endpoints.

To send POST method to your endpoint:
```
$ curl -X POST YOUR_ENDPOINT/blobs --data '{"callback_url": "YOUR_CALLBACK_URL"}'
```

The answer should look like this:
```
{"blob_id": "BLOB_ID", "callback_url": "YOUR_CALLBACK_URL", "upload_url": "UPLOAD_URL"}
```

Save upload_url and blob_id somewhere. Then, go to directory "test_endpoints" and open "upload_file_to_s3_test.py" file.
Put your upload url in UPLOAD_URL variable. For test purposes, I added two blob files in this directory. 
Add path to one of this file into PATH_TO_BLOB variable. 
Feel free to use your blob files and do not forget to add the path to your file. 

After this, run "upload_file_to_s3_test.py" file. The console should display the status code. 
If it is 200, all is well and just wait for a while.

If the status code starts with the number 4 (for example, 400, 404), 
then most likely the upload_url has expired and you will need a new one.

Finally, to send GET method to your endpoint:
```
$ curl -X YOUR_ENDPOINT/blobs/YOUR_BLOB_ID
```

The answer should look like this:
```
{"blob_id": "37d878b7-2d5c-4b42-8dd2-25a0c032d9c5", "labels": [LABELS]}
```