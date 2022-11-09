import json
import os
import requests


def lambda_handler(event, context):
    print("OpenSearch Endpoint", os.environ["PHOTOS_OPENSEARCH_ENDPOINT"])
    print("Received event: " + json.dumps(event, indent=2))
    
    message = 'Hello World! LF2 v3.0'
    return message
