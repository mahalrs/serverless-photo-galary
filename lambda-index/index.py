import json
import requests


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    message = 'Hello World! LF2 v3.0'
    return message
