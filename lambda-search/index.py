import json
import os
import requests
import boto3

from urllib.parse import urlparse
from urllib.parse import parse_qs

from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection


region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = os.environ["PHOTOS_OPENSEARCH_ENDPOINT"]
index = 'photos'

bot_id = os.environ["LEX_BOT_ID"]
bot_alias_id = os.environ["LEX_BOT_ALIAS_ID"]
session_id = 'testuser'


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    #
    # TODO: extract query term from request params
    
    
    lex_req('dog')
    query('file')
    
    res = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            
        },
        'body': json.dumps('message from LF2')
    }
    
    # res = {
    #     'statusCode': 200,
    #     'headers': {'Content-Type': 'application/json'},
    #     'body': 'mybody',
    #     'results': [
    #         {
    #             'url': 'url-to-s3',
    #             'labels': [
    #                 'label1',
    #                 'label2'
    #             ]
    #         }
    #     ]
    # }
    return res


def lex_req(msg):
    client = boto3.client('lexv2-runtime')
    
    res = client.recognize_text(
            botId=bot_id,
            botAliasId=bot_alias_id,
            localeId='en_US',
            sessionId=session_id,
            text=msg)
    
    msg_from_lex = res.get('messages', [])
    print(res)
    print(msg_from_lex)


def query(term):
    q = {
        "size": 5,
        "query": {
            "multi_match": {
                "query": term
            }
        }
    }
    
    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    res = search.search(index=index, body=q)
    print(res)
    #return data
