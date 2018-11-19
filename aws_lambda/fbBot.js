var VERIFY_TOKEN = "my_awesome_token";
var https = require('https');
var PAGE_ACCESS_TOKEN = "YOUR_TOKEN";

function LineBot(mMessage, mReplyToken) {
    var https = require('https');
    var aws = require("aws-sdk");
    var dbClient = new aws.DynamoDB.DocumentClient();
    var lambdaClient = new aws.Lambda({ region: 'us-east-1' });
    
    var myLineToken = PAGE_ACCESS_TOKEN;
    var channelAccessToken = "Bearer " + myLineToken;
    
    var message = mMessage;
    var replyToken = mReplyToken;
    var receiveText = message;
    var replyText = "";
    
    function setReplyMessage(mMessage) {
        console.log("setReplyMessage, argu=" + mMessage);
        replyText = mMessage;
    }
    function appendReplyMessage(mMessage) {
        console.log("appendReplyMessage, argu=" + mMessage);
        replyText += mMessage;
    }
    function checkStringExist(mTarget) {
        return (receiveText.indexOf(mTarget) > -1);
    }
    function launchLambda(mPayload) {
        lambdaClient.invoke({
            FunctionName: 'lineIoTEntryFunc',
            Payload: mPayload
        }, function(error, data) {
            if (error) {
                context.done('error', error);
            }
            if(data.Payload){
                sendResponse();
                //context.succeed(data.Payload)
            }
        });
    }
    function messageProcessing() {
        if(receiveText.startsWith("Speak:")||receiveText.startsWith("Speak:")) {
            console.log(" speak...");
            launchLambda(JSON.stringify({'action': 'speak', 'message': receiveText.substring(6)}));
        } else if(checkStringExist("list")) {
            console.log(" user want to query ZigBee list");
            queryDb();
        } else if(checkStringExist("turn")) {
            var action = "off"
            if(checkStringExist("on")) {
                action = "on"
            } 
            console.log(" user want to turn " + action + " the light");
            setReplyMessage("Okay, I'll turn " + action + " the light");
            launchLambda(JSON.stringify({'action': action}));
        } else if(checkStringExist("reset")) {
            console.log(" user want to reset device");
            setReplyMessage("Okay, I'll reset ZigBee Lighting Device");
            launchLambda(JSON.stringify({'action': 'reset'}));
        } else if(checkStringExist("enable")) {
            console.log(" user want to enable permit join mode");
            setReplyMessage("Okay, I've enable the permit join mode");
            launchLambda(JSON.stringify({'action': 'enable'}));
        } else if(checkStringExist("disable")) {
            console.log(" user want to disable permit join mode");
            setReplyMessage("Okay, I've disable the permit join mode");
            launchLambda(JSON.stringify({'action': 'disable'}));
        } else if(checkStringExist("level")) {
            var step = "low"
            if(checkStringExist("high")) {
                step = "high"
            } else if(checkStringExist("medium")) {
                step = "medium"
            } 
            console.log(" user want to change level to " + step);
            setReplyMessage("Okay, I'll adjust brightness level to " + step);
            launchLambda(JSON.stringify({'action': 'level', 'step' : step}));
        } else if(checkStringExist("color")) {
            var step = "white"
            if(checkStringExist("red")) {
                step = "red"
            } else if(checkStringExist("green")) {
                step = "green"
            } else if(checkStringExist("blue")) {
                step = "blue"
            } 
            console.log(" user want to change level to " + step);
            setReplyMessage("Okay, I'll adjust color to " + step);
            launchLambda(JSON.stringify({'action': 'color', 'step' : step}));
        } 
    }
    function queryDb() {
        console.log("query database...");
        var params = { TableName : "comamierda" };
        dbClient.scan(params, function(err, data) {
            if (err) {
                console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
                setReplyMessage("Unable to query database");
            } else {
                console.log("Query succeeded. data = " + JSON.stringify(data, null, 4));
                setReplyMessage("Here's your ZigBee device list: \r\n");
                data.Items.forEach(function(item) {
                    console.log(" -", item.IEEEAddress + ": " + item.Name);
                    appendReplyMessage("\r\nName: ");
                    appendReplyMessage(item.Name);
                });
                sendResponse();
            }
        });
        
    }
    function sendResponse() {
        sendTextMessage(replyToken, replyText)
    }
    /*
    return {
      setReplyMessage: setReplyMessage,
      appendReplyMessage: appendReplyMessage,
      checkStringExist: checkStringExist,
      launchLambda: launchLambda,
      messageProcessing: messageProcessing,
      queryDb: queryDb,
      sendResponse: sendResponse
   }; */
    return {
      messageProcessing: messageProcessing
   }; 
}





exports.handler = (event, context, callback) => {
    
  // process GET request
  if(event.queryStringParameters){
    var queryParams = event.queryStringParameters;
 
    var rVerifyToken = queryParams['hub.verify_token']
 
    if (rVerifyToken === VERIFY_TOKEN) {
      var challenge = queryParams['hub.challenge']
      
      var response = {
        'body': parseInt(challenge),
        'statusCode': 200
      };
      
      callback(null, response);
    }else{
      var response = {
        'body': 'Error, wrong validation token',
        'statusCode': 422
      };
      
      callback(null, response);
    }
  
  // process POST request
  }else{
    var data = JSON.parse(event.body);
     
    // Make sure this is a page subscription
    if (data.object === 'page') {
    // Iterate over each entry - there may be multiple if batched
    data.entry.forEach(function(entry) {
        var pageID = entry.id;
        var timeOfEvent = entry.time;
        // Iterate over each messaging event
        entry.messaging.forEach(function(msg) {
          if (msg.message) {
            receivedMessage(msg);
          } else {
            console.log("Webhook received unknown event: ", event);
          }
        });
    });
    
    }
    // Assume all went well.
    //
    // You must send back a 200, within 20 seconds, to let us know
    // you've successfully received the callback. Otherwise, the request
    // will time out and we will keep trying to resend.
    var response = {
      'body': "ok",
      'statusCode': 200
    };
      
    callback(null, response);
  }
}

function receivedMessage(event) {
  console.log("Message data: ", event.message);
  
  var senderID = event.sender.id;
  var recipientID = event.recipient.id;
  var timeOfMessage = event.timestamp;
  var message = event.message;
  console.log("Received message for user %d and page %d at %d with message:", senderID, recipientID, timeOfMessage);
  console.log(JSON.stringify(message));
  var messageId = message.mid;
  var messageText = message.text;
  var messageAttachments = message.attachments;
  var isEcho = message.is_echo;
  
    if (isEcho != true && messageText) {
        console.log(" messageText = " + messageText);
        var lb = LineBot(messageText, senderID); 
        lb.messageProcessing();
    
        //Default response
        //sendTextMessage(senderID, messageText);
        
    } else if (messageAttachments) {
        sendTextMessage(senderID, "Message with attachment received");
    }
}

function sendTextMessage(recipientId, messageText) {
  var messageData = {
    recipient: {
      id: recipientId
    },
    message: {
      text: messageText
    }
  };
  callSendAPI(messageData);
}

function callSendAPI(messageData) {
  var body = JSON.stringify(messageData);
  var path = '/v2.6/me/messages?access_token=' + PAGE_ACCESS_TOKEN;
  var options = {
    host: "graph.facebook.com",
    path: path,
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
  };
  var callback = function(response) {
    var str = ''
    response.on('data', function (chunk) {
      str += chunk;
    });
    response.on('end', function () {
 
    });
  }
  var req = https.request(options, callback);
  req.on('error', function(e) {
    console.log('problem with request: '+ e);
  });
 
  req.write(body);
  req.end();
}
