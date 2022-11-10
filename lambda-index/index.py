import json
import os
import boto3

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = 'us-east-1'
HOST = os.environ["PHOTOS_OPENSEARCH_ENDPOINT"]
INDEX = 'photos'


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    metadata = get_metadata(event)
    
    client = OpenSearch(
        hosts = [{'host': HOST, 'port': 443}],
        http_auth = get_awsauth(REGION, 'es'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    # # Delete the index
    # print('Deleting index')
    # print(client.indices.delete(index=INDEX))
    
    client.index(index=INDEX, id=metadata['etag'], body=metadata, refresh=True)
    print(client.get(index=INDEX, id=metadata['etag']))

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from LF1 v3.0')
    }


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key, cred.secret_key, region, service, session_token=cred.token)


def get_metadata(event):
    object_key = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']

    s3client = boto3.client('s3')
    metadata = s3client.head_object(Bucket=bucket, Key=object_key)

    timestamp = metadata['ResponseMetadata']['HTTPHeaders']['last-modified']
    etag = metadata['ResponseMetadata']['HTTPHeaders']['etag']

    custom_labels = get_custom_labels(metadata)
    labels = get_rekognition_labels(bucket, object_key)
    labels.extend(custom_labels)

    return {
        'objectKey': object_key,
        'bucket': bucket,
        'etag': etag,
        'createdTimestamp': timestamp,
        'labels': labels,
    }


def get_custom_labels(metadata):
    labels = []
    if 'x-amz-meta-customlabels' in metadata['ResponseMetadata']['HTTPHeaders']:
        custom_labels = metadata['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
        for label in [x.strip() for x in custom_labels.split(',')]:
            labels.append(label.lower())
    return labels


def get_rekognition_labels(bucket, object_key):
    rekog = boto3.client('rekognition')
    rek_res = rekog.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': object_key}})

    labels = []
    for label in rek_res['Labels']:
        labels.append(label['Name'].lower())

    return labels
