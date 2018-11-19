from __future__ import print_function

import json
import boto3

print('Loading function')

ses = boto3.client('ses')
sns = boto3.client('sns')

askingMailWho = "Who do you want to mail to?"
askingMailContent = "What message do you want to send to?"
responseSendMail = "Already send the mail to"

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print("=================================")
    print("mailEntryFunction >> Received event: " + json.dumps(event))
    print("=================================")

    """ NEED FOLLOWING VARIABLES """
    """
        valCommand = not using
        valCategory = not using
        valUserName = send message to specific user
        valContent = message body

    """
    attributes = ""
    valCommand = ""
    valCategory = ""
    valUserName = ""
    valContent = ""
    hasContent = False
    
    response = {}
    saveAttributes = {}

    """ Get required data from event """
    valCommand = event.get('valCommand')
    valCategory = event.get('valCategory')
    valUserName = event.get('valUserName')
    valContent = event.get('valContent')
    
    if valContent != "UNKNOWN":
        hasContent = True
        
    
    print(" valCommand = " + valCommand)
    print(" valCategory = " + valCategory)
    print(" valUserName = " + valUserName)
    print(" valContent = " + valContent)

    """ mark action is mail """
    saveAttributes['action'] = 'mail'

    """ save need variables """
    if valCommand != "UNKNOWN":
        saveAttributes['valCommand'] = valCommand
    if valCategory != "UNKNOWN":    
        saveAttributes['valCategory'] = valCategory
    if valUserName != "UNKNOWN":
        saveAttributes['valUserName'] = valUserName
    if valContent != "UNKNOWN":
        saveAttributes['valContent'] = valContent
        
    if valUserName == "UNKNOWN":
        response['response'] = askingMailWho
        response['status'] = 'failed'
        response['saveAttributes'] = saveAttributes
        response['keepSession'] = 'true'
    elif hasContent == False:
        response['response'] = askingMailContent
        response['status'] = 'failed'
        response['saveAttributes'] = saveAttributes
        response['keepSession'] = 'true'
    else:
        print("Should send the mail now?")
        doSendMail(valUserName, valContent)
        response['response'] = responseSendMail + " " + valUserName
        response['status'] = 'done'
        response['saveAttributes'] = saveAttributes
        response['keepSession'] = 'false'
        
    return response
    #return { 'message' : '123456'}
    #context.succeed(JSON.parse(response))
    
    #raise Exception('Something went wrong')

def doSendMail(username, content):
    """ default email variable """
    email_addr_to = ""
    email_addr_from = "kenny_pan@xxxxxxxxxxxxxxxxxxxxxxx"
    email_sub = "Message from Bot"
    
    """ translate username to email address """
    if username == "Kenny" or username == "kenny":
        print(username + " mapping address = kenny_pan@xxxxxxxxxxxxxxxxxxxxxx")
        email_addr_to = "MAIL_ADDRESS"
        phone_number = "PHONE_NUMBER"
    
    """ send mail """
    response = ses.send_email(
        Source = email_addr_from,
        Destination={
            'ToAddresses': [
                email_addr_to,
            ]
        },
        Message={
            'Subject': {
                'Data': email_sub
            },
            'Body': {
                'Text': {
                    'Data': content
                 }
            }
        }
    )
    """ send sns """
    sns.publish(
        PhoneNumber = phone_number,
        Message = 'PEGABOT > ' + content
    )
    
    print("--------------------------")
    print(" Send mail")
    print("     From " + email_addr_from)
    print("     To " + email_addr_to)
    print("     Sub " + email_sub)
    print("     Content " + content)
    print("--------------------------")
    #print("Send mail response = " + response)
