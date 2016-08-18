import requests
import json, urllib


SERVER_URL = "http://localhost:5000/webhook"
USER_ID = '1060373100711229'
PAGE_ID = '1611225012509794'


def set_server_url(url):
  SERVER_URL = url

# def send_postback(postback="GETTING_STARTED"):


def send_image():
  msg = message_frame()
  payload = MESSAGE_WITH_IMAGE.copy()
  payload['sender']['id'] = msg['entry'][0]['id']
  # payload['recipient']['id'] = msg['entry'][0]['id']
  msg['entry'][0]['messaging'].append(payload)

  requests.post(url=SERVER_URL, headers=HEADERS, data=json.dumps(msg))

def send_message(text_message = ""):
  msg = message_frame()
  payload = MESSAGE.copy()
  payload['sender']['id'] = msg['entry'][0]['id']
  payload['message']['text'] = text_message
  # payload['recipient']['id'] = msg['entry'][0]['id']
  msg['entry'][0]['messaging'].append(payload)

  requests.post(url=SERVER_URL, headers=HEADERS, data=json.dumps(msg))

def message_frame(user_id = USER_ID):
  msg = MESSAGE_FRAME.copy()
  msg['entry'][0]['id'] = user_id
  return msg


MESSAGE_FRAME = {
  'entry': [
    {
      'id': 'USER_ID',
      'messaging': [
      ]
    }
  ],
  'object': 'page'
}



POSTBACK = {
  "sender": {
    "id": "USER_ID"
  },
  "recipient": {
    "id": "PAGE_ID"
  },
  "timestamp": 1458692752478,
  "postback": {
    "payload": "USER_DEFINED_PAYLOAD"
  }
}

MESSAGE = {
  "sender": {
    "id": "USER_ID"
  },
  "recipient": {
    "id": "PAGE_ID"
  },
  "timestamp": 1458692752478,
  "message": {
    "mid": "mid.1457764197618:41d102a3e1ae206a38",
    "seq": 73,
    "text": "",
    "quick_reply": {
      "payload": "DEVELOPER_DEFINED_PAYLOAD"
    }
  }
}

MESSAGE_WITH_IMAGE = {
  "sender": {
    "id": "USER_ID"
  },
  "recipient":{
    "id": "PAGE_ID"
  },
  "timestamp": 1458692752478,
  "message":{
    "mid": "mid.1458696618141:b4ef9d19ec21086067",
    "seq": 51,
    "attachments": [
      {
        "type": "image",
        "payload": {
          "url": "https://scontent.xx.fbcdn.net/v/t35.0-12/14045457_1430017397015062_622059024_o.jpg?_nc_ad=z-m&oh=a35554e821dfc0ec310605aa2eecea2f&oe=57B82967"
        }
      }
    ]
  }
}

HEADERS = {
  "Content-Type": "application/json"
}

