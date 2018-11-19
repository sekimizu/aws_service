# Amazon Web Service function code

The Git repository for AQUA ASW service.

## Lambda (aws_lambda folder)

### fbBot.js (Node.js 4.3)

* Webhook callback function to accept FB messenger passed message
(Webhook URL: https://(xxxxxxxxx).execute-api.us-east-1.amazonaws.com/dev2/fbBOT)

```
FB server -> Amazon API Gateway -> fbBot.js
```

### lineBot.js (Node.js 4.3)

* Webhook callback function to accept Line messenger API passed message
(Webhook URL: https://(xxxxxxxxxxx).execute-api.us-east-1.amazonaws.com/dev2/lineBOT)

```
Line server -> Amazon API Gateway -> lineBot
```

### lineIoTFunction.py (Python 2.7)

* Execution function to handle event comes from "fbBot.js" and "lineBot.js".
Call AWS IoT to perform actually execution, and return message back to the bot.

```
fbBot    \
         +-- lineIoTFunction --> AWS IoT broker
lineBot  /
```


### EntryFunction.py (Python 2.7)

* Handle AVS Skill function callback

```
AVS client -> AVS -> Skill -> EnterFunction
```

### IoTEntryFunction.py (Python 2.7)

* Handle IoT event (ZigBee/IR) comes from EntryFunction

```
EntryFunction -> IoTEntryFunction
```

### mailEntryFunction.py (Python 2.7)

* Handle mail & SNS event comes from EntryFunction

```
EntryFunction -> mailEntryFunction
```

### updateDevListDb.py (Python 2.7)

* Handle device scan list which reported by TX2 ZStack, and record it into AWS DB

```
TX2 MQTT client -> AWS IoT broker -> updateDevListDb -> Amazon DynamoDB
```

### updateDevPairDb.py (Python 2.7)

* Handle device join ZigBee network list which reported by TX2 ZStack, and record it into AWS DB

```
TX2 MQTT client -> AWS IoT broker -> updateDevPairDb -> Amazon DynamoDB
```




