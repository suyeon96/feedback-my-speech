import json
import boto3
import requests
import datetime as dt
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection

PI_LEDON_URL = 'http://xxx.xxx.xxx.xxx/led' # raspberry pi web url for turn on led

def detect_faces(photo, bucket):
    client=boto3.client('rekognition')
    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},Attributes=['ALL'])

    return response['FaceDetails']


def index_document(item):
    es_endpoint = 'search-fs-elasticsearch-xur5mz64m7a2rb3jlny6hoxrdq.ap-northeast-2.es.amazonaws.com'
    es_index = "index-image"
    currenttime = dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    person_cnt = len(item)
    sleep_cnt = 0
    print(f'size : {person_cnt}')

    # use this code when using arn authentication
    session = boto3.session.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    awsauth = AWSRequestsAuth(
            aws_access_key=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_token=credentials.token,
            aws_host=es_endpoint,
            aws_region=session.region_name,
            aws_service='es'
        )

    # elasticsearch connection
    es = Elasticsearch(
            hosts=[{'host': es_endpoint, 'port': 443}],
            # http_auth=awsauth,
            http_auth=('fs-admin', 'New1234!'),
            use_ssl=True,
            verify_certs=True,
            # ca_certs=certifi.where(),
            connection_class=RequestsHttpConnection
        )
    
    # index new document to elasticsearch
    for x in item:
        doc = {
            "age" : (x['AgeRange']['Low'] + x['AgeRange']['High']) / 2,
            "gender" : x['Gender']['Value'],
            "smile" : x['Smile']['Value'],
            "emotion" : x['Emotions'][0]['Type'],
            "eyeopen" : x['EyesOpen']['Value'],
            "@timestamp" : currenttime
        }
        es.index(index=es_index, body=doc)
        
        if not x['EyesOpen']['Value']:
            sleep_cnt += 1
    
    # turn on led(warning) when half of listeners is sleep
    if (sleep_cnt > person_cnt/2) or (sleep_cnt==1 and person_cnt==1):
        print(f'sleep count : {sleep_cnt}')
        response = requests.get(url=PI_LEDON_URL)
        print(f'pi response : {response.status_code}')


def lambda_handler(event, context):
    print(f'start : {event}')
    
    try:
        # get image frame to s3 bucket
        body = json.loads(event['Records'][0]['body'])
        bucket_name = body['Records'][0]['s3']['bucket']['name']
        filename_key = body['Records'][0]['s3']['object']['key']
        print(f'bucketName : {bucket_name}, filenameKey : {filename_key}')
        
        # facial analysis using amazon rekognition
        reko_response = detect_faces(filename_key, bucket_name)
        # print(f'response : {response}')
        
        index_document(reko_response)
        
    except Exception as e:
        print(e)
    
    return {'statusCode': 200}
