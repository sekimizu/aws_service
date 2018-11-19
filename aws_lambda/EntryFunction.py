import json
import boto3

print('Loading entry function')

class AVSHandler:
    def __init__(self, attribute = {}, slots = {}):
        self.unknown = "UNKNOWN"
        self.attribute = attribute
        self.slots = slots
        self.action = self.unknown
        self.category = self.unknown
        self.command = self.unknown
        self.username = self.unknown
        self.content = self.unknown
        self.keepSession = False
        self.reportAttr = {}
        self.lambdaClient = boto3.client('lambda')
        self.lambdaServer = {
            'mail' : 'mailEntryFunc',
            'light' : 'iotEntryFunc'
        }

    def loadFromAttributeOrSlot(self, key):
        if key in self.attribute:
            return self.attribute.get(key)
        elif key in self.slots and 'value' in self.slots.get(key):
            return self.slots.get(key).get('value')
        return self.unknown

    def launchLambdaFunc(self):
        print(" >>> " + self.action)
        
        self.attribute['action'] = self.action
        self.attribute['category'] = self.category
        self.attribute['command'] = self.command
        self.attribute['username'] = self.username

        resp = Response()
        lambdaclient = LambdaClient()
        lambdaclient.setConnectServer(self.lambdaServer[self.action])
        lambdaclient.setArgument(self.attribute)
        lambdaclient.connect()
        result = lambdaclient.getResult()

        resp.setOutputText(result['response'])
        resp.setReportAttr(result['saveAttributes'])
        
        if result['keepSession'] == "true":
            resp.setShouldEndSession(False)
        return resp.buildResp()

class LambdaClient:
    def __init__(self):
        self.client = boto3.client('lambda')
        #self.connectType = "Event"
        self.connectServer = ""
        self.connectType = "RequestResponse"
        self.invokeResponse = ""
        self.result = {}
        self.argument = {}
    
    def connect(self):
        self.invokeResponse = self.client.invoke(
            FunctionName = self.connectServer,
            InvocationType = self.connectType, 
            Payload = json.dumps(self.argument)
        )
        if self.invokeResponse != "":
            responseRata = self.invokeResponse['Payload'].read().decode()
            if responseRata != "":
                tempStr = json.dumps(responseRata).replace('\\', '')
                self.result = json.loads(tempStr[1:-1])
    
    def setConnectServer(self, connectServer):
        self.connectServer = connectServer

    def setArgument(self, argument = {}):
        self.argument = argument

    def getResult(self):
        return self.result

class Response:
    def __init__(self):
        self.unknown = ""
        self.title = self.unknown
        self.outputText = self.unknown
        self.repromptText = self.unknown
        self.shouldEndSession = True
        self.reportAttr = {}
        self.defaultResp = {}
        self.loadDefaultResp()

    def loadDefaultResp(self):
        self.defaultResp["do_not_understand"] = "Sorry, I don't understand what you talking"
        self.defaultResp["try_again"] = "Please specify the command more clearly and try again"

    def setOutputText(self, outputText):
        self.outputText = outputText

    def setRepromptText(self, repromptText):
        self.repromptText = repromptText

    def setShouldEndSession(self, shouldEndSession):
        self.shouldEndSession = shouldEndSession

    def setReportAttr(self, reportAttr):
        self.reportAttr = reportAttr

    def buildRespContent(self):
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': self.outputText
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': self.repromptText
                }
            },
            'shouldEndSession': self.shouldEndSession                                                           
        } 

    def buildResp(self):
        return {
            'version': '1.0',
            'sessionAttributes': self.reportAttr,
            'response': self.buildRespContent()
        }

def lambda_handler(event, context):
    print("=================================")
    print("EntryFunction Received event: " + json.dumps(event))
    print("=================================")

    requestType = event['request']['type']        
    print(" Request Type = " + requestType)

    if requestType == "LaunchRequest":
        return onLaunchRequest(event['request']['intent'], event['session'])
    elif requestType == "IntentRequest":
        return onIntentRequest(event['request']['intent'], event['session'])
    else:
        raise Exception('Something went wrong')

def onLaunchRequest(request, session):
    return responseDefaultUnknowCommand()
    
def onIntentRequest(intent, session):

    print("onIntentRequest is called")

    sessionAttributes = {}
    if 'attributes' in session:
        sessionAttributes = session.get('attributes')
	
    intentName = intent['name']
    intentSlots = intent['slots']
    
    if intentName == "ContentIntent":
        print(" --> ContentIntent")
    elif intentName == "MainIntent":
        print(" --> MainIntent")
    else:
        return responseDefaultUnknowCommand()

    # Launch AVSClient here!!!	
    avsHandler = AVSHandler(sessionAttributes, intentSlots) 

    avsHandler.action = avsHandler.loadFromAttributeOrSlot('action')
    avsHandler.category = avsHandler.loadFromAttributeOrSlot("category")
    avsHandler.command = avsHandler.loadFromAttributeOrSlot("command")
    avsHandler.username = avsHandler.loadFromAttributeOrSlot("username")

    #return responseDefaultUnknowCommand()
    if avsHandler.category in avsHandler.lambdaServer:
        avsHandler.action = avsHandler.category
    elif avsHandler.command in avsHandler.lambdaServer:
        avsHandler.action = avsHandler.command
    else:
        print(" not support category or command")
        return responseDefaultUnknowCommand()
    
    return avsHandler.launchLambdaFunc()

""" tell user that we can't find command and category in intent """
def responseDefaultUnknowCommand():
    resp = Response()
    resp.setOutputText(resp.defaultResp["do_not_understand"])
    resp.setRepromptText(resp.defaultResp["try_again"])
    resp.setReportAttr = {}
    return resp.buildResp()
