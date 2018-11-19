import json
import boto3

iotClient = boto3.client('iot-data')
zigbeeAddress = "0x000D6F0005076786"

askingLightOnOff = "Do you want to turn on or turn off the light?"
responseLightOn = "The light had been turn on"
responseLightOff = "The light had been turn off"

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print("=================================")
    print("iotEntryFunc >> Received event: " + json.dumps(event))
    print("=================================")

    """ NEED FOLLOWING VARIABLES """
    """
        valCommand = on / off
        valCategory = light / IR
        valTrigger = previos action stored in attributes
        
    """

    valCommand = ""
    valCategory = ""
    valTrigger = "UNKNOWN"
    hasTrigger = False
    
    valTopic = ""

    response = {}
    saveAttributes = {}

    """ Get required data from event """
    if 'valCommand' in event:
        valCommand = event.get('valCommand')
    if 'valCategory' in event:    
        valCategory = event.get('valCategory')
    if 'valTrigger' in event:
        valTrigger = event.get('valTrigger')
        hasTrigger = True

    """ use valCommand to decide valTrigger's value if attribute didn't present it """
    if hasTrigger == False:
        if valCommand.find('ON') >= 0 or valCommand.find('on') >= 0:
            valTrigger = "on"
        elif valCommand.find('OFF') >= 0 or valCommand.find('off') >= 0:
            valTrigger = "off"

    print(" valCommand = " + valCommand)
    print(" valCategory = " + valCategory)
    print(" valTrigger = " + valTrigger)

    print(" Target = " + valCategory + ", Switch to " + valTrigger)
    
    """ save need variables """
    saveAttributes['action'] = 'iot'
    if valCommand != "UNKNOWN":
        saveAttributes['valCommand'] = valCommand
    if valCategory != "UNKNOWN":    
        saveAttributes['valCategory'] = valCategory
    if valTrigger != "UNKNOWN":  
        saveAttributes['valTrigger'] = valTrigger
    
    
    """ decide action """
    if valTrigger == "UNKNOWN":
        response['response'] = askingLightOnOff
        response['status'] = 'failed'
        response['saveAttributes'] = saveAttributes
        response['keepSession'] = 'true'
    elif valTrigger == "on":
        response['response'] = responseLightOn
    elif valTrigger == "off":
        response['response'] = responseLightOff
        
    response['status'] = 'done'
    response['saveAttributes'] = saveAttributes
    response['keepSession'] = 'false'
    
    triggerLightOnOff(valTrigger)
        
    return response
    #return { 'message' : '123456'}
    #context.succeed(JSON.parse(response))
    #raise Exception('Something went wrong')

def triggerLightOnOff(valTrigger):
    if valTrigger == "on":
        valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0006/0x01/0x0000"
        print(" publish iot message to " + valTopic)
        response = iotClient.publish(
            topic = valTopic,
            qos = 0,
            payload = json.dumps({"foo":"bar"}))
    else:
        valTopic = "zigbee/cmd/" + zigbeeAddress + "/0x0006/0x00/0x0000"
        print(" publish iot message to " + valTopic)
        response = iotClient.publish(
            topic = valTopic,
            qos = 0,
            payload=json.dumps({"foo":"bar"}))
    
    
    
    
    
