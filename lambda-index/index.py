import json
import requests
import boto3
import os

from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection


region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = os.environ["PHOTOS_OPENSEARCH_ENDPOINT"]
index = 'photos'


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    object_key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    timestamp = event['Records'][0]['eventTime']
    
    s3client = boto3.client('s3')
    metadata = s3client.head_object(Bucket=bucket, Key=object_key)
    print(metadata)
    #
    # TODO: get custom labels from metadata
    #
    
    rekog = boto3.client('rekognition')
    rek_res = rekog.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': object_key}})
    labels = rek_res['Labels']
    print(labels)
    #
    # TODO: extract label names from labels
    #
    
    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    document = {
        'objectKey': object_key,
        'bucket': bucket,
        'createdTimestamp': timestamp,
        'labels': [
            'page',
            'text',
            'file'
        ]
    }
    
    search.index(index=index, doc_type='_doc', id=timestamp, body=document)
    print(search.get(index=index, doc_type='_doc', id=timestamp))
    
    message = 'Hello World! LF1 v3.0'
    return message
