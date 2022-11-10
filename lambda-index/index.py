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

    s3client = boto3.client('s3')
    metadata = s3client.head_object(Bucket=bucket, Key=object_key)
    print(metadata)
    
    # timestamp = metadata['ResponseMetadata']['HTTPHeaders']['last-modified']
    timestamp = event['Records'][0]['eventTime']
    labels = []
    
    if 'x-amz-meta-customLabels' in metadata['ResponseMetadata']['HTTPHeaders']:
        custom_labels = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customLabels']
        #
        # TODO: split custom labels and add to labels
        #

    rekog = boto3.client('rekognition')
    rek_res = rekog.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': object_key}})
    print(rek_res['Labels'])
    
    for l in rek_res['Labels']:
        labels.append(l['Name'].lower())
    
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
        'labels': labels
    }
    print(document)
    
    search.index(index=index, id=timestamp, body=document, refresh=True)
    print(search.get(index=index, id=timestamp))
    
    message = 'Hello World! LF1 v3.0'
    return message
