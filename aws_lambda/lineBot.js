function LineBot(mMessage, mReplyToken) {
    var https = require('https');
    var aws = require("aws-sdk");
    var dbClient = new aws.DynamoDB.DocumentClient();
    var lambdaClient = new aws.Lambda({ region: 'us-east-1' });
    
    var myLineToken = "TOKEN";
    var channelAccessToken = "Bearer " + myLineToken;
    
    var message = mMessage;
    var replyToken = mReplyToken;
    var receiveText = message.text;
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
            setReplyMessage("Speak " + receiveText.substring(6) + " from Bot...");
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
        } else {
            console.log("echo...");
            setReplyMessage(receiveText);
            sendResponse();
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
        console.log("sendResponse...");
        var request_body = JSON.stringify({
            replyToken: replyToken,
            messages:[
                {
                    "type" : "text",
                    "text" :  replyText
                }
            ]
        });
        var req = https.request({
            hostname: "api.line.me",
            port: 443,
            path: "/v2/bot/message/reply",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(request_body),
                "Authorization": channelAccessToken
            }
        });
        req.end(request_body, (err) => {
            err && console.log(err);
        });
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
    console.log(" EVENT >>> " + JSON.stringify(event, null, 4));
    
    body = event.body;
    json_body = JSON.parse(body)
    event_body = json_body.events[0];
    
    var lb = LineBot(event_body.message, event_body.replyToken); 
    lb.messageProcessing();
}
