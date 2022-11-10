import json
import os
import boto3

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = 'us-east-1'

BOT_ID = os.environ["LEX_BOT_ID"]
BOT_ALIAS_ID = os.environ["LEX_BOT_ALIAS_ID"]
BOT_SESSION_ID = 'testuser'

HOST = os.environ["PHOTOS_OPENSEARCH_ENDPOINT"]
INDEX = 'photos'


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
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
        'body': json.dumps('Hello from LF2'),
        'results': results
    }


def parse_query(user_query):
    # client = boto3.client('lexv2-runtime')
    # res = client.recognize_text(
    #         botId=BOT_ID,
    #         botAliasId=BOT_ALIAS_ID,
    #         localeId='en_US',
    #         sessionId=BOT_SESSION_ID,
    #         text=user_query)
    
    # #
    # # TODO: parse lex response and return query terms.
    # #       toknize term to handle plural.
    # #       return empty list if invalid query.
    # #
    # msg_from_lex = res.get('messages', [])
    # print(res)
    # print(msg_from_lex)
    return [user_query]


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
