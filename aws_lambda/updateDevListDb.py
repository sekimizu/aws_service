from __future__ import print_function

import time
from datetime import datetime
import json
import boto3

dynamodb = boto3.resource('dynamodb')

print('Loading function')

def lambda_handler(event, context):
    print("=================================")
    print("updateDevListDb >> Received event: " + json.dumps(event))
    print("=================================")

    total = event['total']
    
    print("Total " + total + " items in the list")
    
    deviceList = event['deviceid']
    
    print("Device List = " + json.dumps(deviceList))
    
    for item in deviceList:
        print(str(item))
        devId = str(item)[3:21]
        print(" --> " + devId)
        print("active = " + item[devId]['active'])
        print("brand = " + item[devId]['brand'])
        print("model = " + item[devId]['model'])
        print("name = " + item[devId]['name'])
        
        if item[devId]['active'] == "1":
            devActive = True
        else:
            devActive = False
        
        table = dynamodb.Table('comamierda')
        time.ctime() 
        item = {
            'IEEEAddress': devId,
            'Name': str(item[devId]['name']),
            'Brand': str(item[devId]['brand']),
            'Model': str(item[devId]['model']),
            'Active': devActive,
            'UpdateTime': str(time.ctime())
        }

        # write the todo to the database
        table.put_item(Item=item)

        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }
        print("response = " + str(response))
    

    

