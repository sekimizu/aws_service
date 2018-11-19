from __future__ import print_function

import time
from datetime import datetime
import json
import boto3

dynamodb = boto3.resource('dynamodb')

print('Loading function')

def lambda_handler(event, context):
    print("=================================")
    print("updateDevPairDb >> Received event: " + json.dumps(event))
    print("=================================")

    ieeeaddress = event['id']
    manufacture = event['manufacture']
    cluster = event['cluster']
    model = event['model']
    name = event['name']
    
    table = dynamodb.Table('hijodeputa')
    
    time.ctime() 

    print("time=" + str(time.ctime()))

    item = {
        'IEEEAddress': str(event['id']),
        'Name': str(event['name']),
        'Manufacture': str(event['manufacture']),
        'Model': str(event['model']),
        'Cluster': str(event['cluster']),
        'Active': True,
        'JointTime': str(time.ctime())
    }

    # write the todo to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }
    print("response = " + str(response))
