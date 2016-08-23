# -*- coding: utf-8 -*-
import json, urllib, requests, tempfile, os, uuid
from flask import Flask, request, abort, send_from_directory
from PIL import Image
from StringIO import StringIO

# required to post an image to facebook
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
import urllib2
from pymessenger.bot import Bot
from pymessenger import Element, Button

register_openers()

app = Flask(__name__)

access_token = 'EAAPlE5lfeCwBADurnmtjJWiXFxZBImpdZAPTi1hb9ZAJzxhjoZBy2lfXMEmTBWLWZA6ytpXnTsSHvPJN9OD9wxaPdXmLDjehGI6DhSCpxqzQM240Wx645elKeB2TB2p7PCFB3nKTDwirclZCZBZAawFoIoRiuj5u3OLdUPk5ivnyjwZDZD'
bot = Bot(access_token)
server_url = "https://b118db1f.ngrok.io"

DB_FILE = "data.json"
with open(DB_FILE) as data_file:
  user_db = json.load(data_file)

TEMPLATES = [
    "vdb_badge1", "vdb_badge2", "vdb_badge3",
]


@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

@app.route("/", methods=["GET"])
def root():
    return "Hello World!"


# webhook for facebook to initialize the bot
@app.route('/webhook', methods=['GET'])
def get_webhook():
    if not 'hub.verify_token' in request.args or not 'hub.challenge' in request.args:
        abort(400)

    return request.args.get('hub.challenge')


@app.route('/webhook', methods=['POST'])
def post_webhook():
    data = request.json
    print "################# INCOMING DATA"
    print data
    if data["object"] == "page":
        for entry in data['entry']:
            for messaging_event in entry['messaging']:

                if "message" in messaging_event:

                    sender_id = messaging_event['sender']['id']

                    if sender_id not in user_db:
                      user_db[sender_id] = {
                        "status": "NEW",
                        "template": "vdb_badge1"
                      }
                    save_db()


                    if 'attachments' in messaging_event['message']:
                        if messaging_event['message']['attachments'][0]['type'] == 'image':
                            url = messaging_event['message']['attachments'][0]['payload']['url']
                            img = Image.open(StringIO(requests.get(url).content))
                            reply_with_selfie_drafts(sender_id, img)


                    if 'text' in messaging_event['message']:
                        message_text = messaging_event['message']['text']
                        send_templates(sender_id)

                if "postback" in messaging_event:
                    sender_id = messaging_event['sender']['id']
                    postback = messaging_event['postback']['payload']
                    received_postback(sender_id, postback)

    return "ok", 200

def received_postback(sender_id, postback):
    print "GOT POSTBACK: " + postback
    user_db[sender_id]["template"] = postback
    bot.send_text_message(sender_id, "Vorlage gewählt :)")
    # if 'GETTING_STARTED' in postback:
        # bot.send_text_message(sender_id,"Hi! Schick mir einen Selfie :)")

def send_templates(recipient_id):
    templates = []

    for temp in TEMPLATES:
        templates.append(Element(
            title="Vorlage",
            image_url=asset_url(temp + "_preview.jpg"),
            subtitle="Vorlage",
            buttons=[Button({
                "type": "postback",
                "title": "Vorlage wählen",
                "payload": temp
            })]
        ))

    bot.send_generic_message(recipient_id, templates)
def reply_with_selfie_drafts(recipient_id, img):
    badge = Image.open("assets/" + user_db[recipient_id]["template"] + ".png")
    badge.thumbnail(img.size)

    # pasting badge on bottom right edge
    img.paste(badge,
              (img.size[0] - badge.size[0], img.size[1] - badge.size[1]),
              badge)

    temp_filepath = 'assets/selfie-' + str(uuid.uuid4()) + '.jpg'
    img.save(temp_filepath)

    params = {
        "access_token": access_token
    }

    data = {
        "recipient[id]": recipient_id,
        "message[attachment][type]": "image",
        "message[attachment][payload][]": ""
    }
    items = []

    for name, value in data.items():
        items.append(MultipartParam(name, value))
    items.append(MultipartParam.from_file("file", temp_filepath))

    url = "https://graph.facebook.com/v2.6/me/messages?" + urllib.urlencode(params)

    datagen, headers = multipart_encode(items)
    request = urllib2.Request(url, datagen, headers)
    print "#### REQUEST"
    response = urllib2.urlopen(request)

    print response.read()
    os.remove(temp_filepath)

def get_url(url):
    result = request.get(url)
    return json.loads(result.content)


def do_rules(recipient_id, message_text):
    rules = {
        "Hello": "World",
        "Foo": "Bar"
    }

    if message_text in rules:
        reply_with_text(recipient_id, rules[message_text])

    else:
        reply_with_text(recipient_id, "You have to write something I understand ;)")


def reply_with_text(recipient_id, message_text):
    message = {
        "text": message_text
    }
    reply_to_facebook(recipient_id, message)


def reply_with_generic_template(recipient_id, elements):
    message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": elements
            }
        }
    }
    reply_to_facebook(recipient_id, message)


def reply_to_facebook(recipient_id, message):
    params = {
        "access_token": access_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": message
    })

    print "################# PRINTING RESPONSE DATA"
    print data

    url = "https://graph.facebook.com/v2.6/me/messages?" + urllib.urlencode(params)
    r = requests.post(url=url, headers=headers, data=data)


def create_generic_template_element(title, image_url, subtitle):
    return {
        "title": title,
        "image_url": image_url,
        "subtitle": subtitle
    }

def save_db():
  with open('data.json', 'w') as data_file:
    json.dump(user_db, data_file)

def asset_url(asset):
    return server_url + "/assets/" + asset
