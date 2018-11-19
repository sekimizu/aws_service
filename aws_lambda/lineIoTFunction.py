import json
import boto3

iotClient = boto3.client('iot-data')
zigbeeAddress = "0x0017880100FA29A4"
#zigbeeAddress = "0x0017880100FDCEC3"

askingLightOnOff = "Do you want to turn on or turn off the light?"
responseLightOn = "The light had been turn on"
responseLightOff = "The light had been turn off"

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print("=================================")
    print("lineIoTEntryFunc >> Received event: " + json.dumps(event))
    print("=================================")

    response = "OK"
    action = event['action']
    
    """
    For voice
    """
    #enableJoin(action)
    
    if action == "reset":
        resetLighting()
    elif action == "on":
        triggerLightOn()
    elif action == "off":
        triggerLightOff()
    elif action == "enable":
        enableJoin()
    elif action == "disable":
        disableJoin()
    elif action == "level":
        step = event['step']
        print(" Adjust level to " + step)
        adjustLevel(step)
    elif action == "color":
        step = event['step']
        print(" Adjust color to " + step)
        adjustColor(step)
    elif action == "speak":
        message = event['message']
        print(" User speak :" + message)
        userSpeak(message)
    
    
    return response
    #return { 'message' : '123456'}
    #context.succeed(JSON.parse(response))
    #raise Exception('Something went wrong')

def userSpeak(message):
    valTopic = "zigbee/pair/enable"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = message)

def enableJoin(action):
    valTopic = "zigbee/pair/enable"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = "NO")

def disableJoin():
    valTopic = "zigbee/pair/exit"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))

def resetLighting():
    valTopic = "zigbee/pair/reset"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))

def adjustLevel(step):
    if step == "high":
        num = "FF"
    elif step == "medium":
        num = "80"
    else:
        num = "00"
        
    valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0008/0x00/0x" + num + "0000"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))

"""
Red:
/asrock/x10/[SID]/zigbee/cmd/[DeviceID]/0x0300/0x07/0xA33754240000
Green:
/asrock/x10/[SID]/zigbee/cmd/[DeviceID]/0x0300/0x07/0x4C7F98FF0000
Blue:
/asrock/x10/[SID]/zigbee/cmd/[DeviceID]/0x0300/0x07/0x26400F4D0000
White:
/asrock/x10/[SID]/zigbee/cmd/[DeviceID]/0x0300/0x07/0x4FBD53E40000

0x0300/0x09/0x000100010000
"""
def adjustColor(step):
    if step == "red":
        num = "0xA33754240000"
    elif step == "green":
        num = "0x4C7F98FF0000"
    elif step == "blue":
        num = "0x26400F4D0000"
    else:
        num = "0x4FBD53E40000"
        
    valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0300/0x07/" + num
    
    #valTopic = "zigbee/cmd/" + zigbeeAddress + "0x0300/0x09/0x000100010000"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))


def triggerLightOn():
    valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0006/0x01/0x0000"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))
        
def triggerLightOff():
    valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0006/0x00/0x0000"
    print(" publish iot message to " + valTopic)
    response = iotClient.publish(
        topic = valTopic,
        qos = 0,
        payload = json.dumps({"foo":"bar"}))
        

    
    
