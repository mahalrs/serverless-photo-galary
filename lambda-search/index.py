import json
import os

import boto3
import inflection as inf

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = os.environ['REGION']

BOT_ID = os.environ['LEX_BOT_ID']
BOT_ALIAS_ID = os.environ['LEX_BOT_ALIAS_ID']
BOT_SESSION_ID = 'testuser'

HOST = os.environ['PHOTOS_OPENSEARCH_ENDPOINT']
INDEX = os.environ['PHOTOS_OPENSEARCH_INDEX']


def lambda_handler(event, context):
    print('Received event: ' + json.dumps(event))
    
    user_query = event['queryStringParameters']['q']
    query_terms = parse_query(user_query)
    
    results = []
    if query_terms:
        results = get_results(query_terms)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'results': results})
    }


def parse_query(user_query):
    client = boto3.client('lexv2-runtime')
    res = client.recognize_text(
            botId=BOT_ID,
            botAliasId=BOT_ALIAS_ID,
            localeId='en_US',
            sessionId=BOT_SESSION_ID,
            text=user_query)
    print(res)
    
    keywords = res['messages'][0]['content'].split(',')
    keywords = set([inf.singularize(k.lower()) for k in keywords])
    print(keywords)
    return list(keywords)


def get_results(query_terms):    
    hits = []
    for q in query_terms:
        hits.extend(query(q))
    
    results = []
    for hit in hits:
        url = get_s3_url(hit['bucket'], hit['objectKey'])
        results.append({
            'url': url,
            'labels': hit['labels']
        })
    return results


def query(term):
    q = {
        'size': 5,
        'query': {
            'multi_match': {
                'query': term,
                'fields': ['labels', 'objectKey']
            }
        }
    }
    # q = {
    #     'size': 5,
    #     'query': {
    #         'fuzzy': {
    #             'labels': {
    #                 'value': term,
    #                 'fuzziness': 2,
    #             }
    #         }
    #     }
    # }
    
    client = OpenSearch(
        hosts = [{'host': HOST, 'port': 443}],
        http_auth = get_awsauth(REGION, 'es'),
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    res = client.search(index=INDEX, body=q)
    print(res)
    hits = res['hits']['hits']
    results = []
    
    for hit in hits:
        results.append(hit['_source'])
    
    return results


def get_s3_url(bucket, key):
    client = boto3.client('s3')
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=3600)


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key, cred.secret_key, region, service, session_token=cred.token)
