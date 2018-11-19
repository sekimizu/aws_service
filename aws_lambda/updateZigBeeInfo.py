from __future__ import print_function

import json
import boto3
import time

dynamodb = boto3.resource('dynamodb')

print('Loading function')

def lambda_handler(event, context):
    
    table = dynamodb.Table('zigbeeInfo')
    timestamp = int(time.time() * 1000)
    item = {
        'id': str("HELLO WORLD!!!"),
        'text': str("222This is message body of this test sample!!!"),
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # write the todo to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    print("response = " + str(response))
