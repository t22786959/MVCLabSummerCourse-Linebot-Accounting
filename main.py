'''
This is my LineBot API
How to Start:
    > Step 0. Go to ./MVCLab-Summer-Course/LineBot/
        > cd ./MVCLab-Summer-Course/LineBot
    > Step 1. Install Python Packages
        > pip install -r requirements.txt
    > Step 2. Run main.py
        > python main.py
Reference:
1. LineBot API for Python
    > https://github.com/line/line-bot-sdk-python
2. Pokemon's reference
    > https://pokemondb.net/pokedex/all
3. Line Developer Messaging API Doc
    > https://developers.line.biz/en/docs/messaging-api/
'''
import os
import re
import json
import random
from dotenv import load_dotenv
from pyquery import PyQuery
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from influxdb import InfluxDBClient
"""
init DB
"""
class DB():
    def __init__(self, ip, port, user, password, db_name):
        self.client = InfluxDBClient(ip, port, user, password, db_name) 
        print('Influx DB init.....')

    def insertData(self, data):
        """
        [data] should be a list of datapoint JSON,
        "measurement": means table name in db
        "tags": you can add some tag as key
        "fields": data that you want to store
        """
        if self.client.write_points(data):
            return True
        else:
            print('Falied to write data')
            return False

    def queryData(self, query):
        """
        [query] should be a SQL like query string
        """
        return self.client.query(query)

# Init a Influx DB and connect to it
db = DB('127.0.0.1', 8086, 'root', '', 'accounting_db')

load_dotenv() # Load your local environment variables

# Pokedex Link
pokemons_link = 'https://pokemondb.net/pokedex/all'
# Get all info from link (html)
doc = PyQuery(url=pokemons_link).find('td').find('span').children()
# Create My_pokedex Images Dict
pokemons_imgs = dict()
# For filter the empty image from link
empty_img_url = 'https://img.pokemondb.net/s.png'
# Add each pokemon img url into dict
for poke in doc:
    poke = PyQuery(poke)
    # Filter empty img
    if not re.match(poke.attr('data-src'), empty_img_url):
        poke_url = poke.attr('data-src') # Attribute['data-src'] value
        poke_name = str(poke_url).split('/')[-1][:-4].lower() # Get lower case of a pokemon name & filter .png behind
        # Save a pokemon's img info
        pokemons_imgs[poke_name] = poke_url

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

app = FastAPI()

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

'''
For first testing, you can comment the code below after you check your linebot can send you the message below
'''
#CHANNEL_ID = os.getenv('LINE_UID') # For any message pushing to or pulling from Line Bot using this ID
# My_LineBotAPI.push_message(CHANNEL_ID, TextSendMessage(text='Welcome to my pokedex !')) # Push a testing message

# Events for message reply
my_event = [ '#note', '#report', '#delete', '#sum']
# My pokemon datas
my_pokemons = dict()
poke_file = 'my_pokemons.json'
# Load local json file if exist
if os.path.exists(poke_file):
    with open(poke_file, 'r') as f:
        my_pokemons = json.load(f)

'''
See more about Line Emojis, references below
> Line Bot Free Emojis, https://developers.line.biz/en/docs/messaging-api/emoji-list/
'''
# Create my emoji list
my_emoji = [
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'005'}],
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'019'}],
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'096'}]
]

# Line Developer Webhook Entry Point
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and 
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')
    return 'OK'

# All message events are handling at here !
@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
  
    # Split message by white space
    recieve_message = str(event.message.text).split(' ')
    # Get first splitted message as command
    case_ = recieve_message[0].lower().strip()
    # Help command for listing all commands to user
    if re.match(my_event[0], case_):
        if len(recieve_message)!=4:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Command Wrong!"
                )
            )

        # cmd: #note [事件] [+/-] [錢]
        event_ = recieve_message[1]
        op = recieve_message[2]
        money = int(recieve_message[3])
        # process +/-
        if op == '-':
            money *= -1
        # get user id
        user_id = event.source.user_id
       
        # build data
        data = [
            {
                "measurement" : "accounting_items",
                "tags": {
                    "user": str(user_id),
                    # "category" : "food"
                },
                "fields":{
                    "event": str(event_),
                    "money": money
                }
            }
        ]
        if db.insertData(data):
            # successed
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Write to DB Successfully!"
                )
            )

    elif re.match(my_event[1], case_):
        # get user id
        user_id = event.source.user_id
        query_str = """
        select * from accounting_items 
        """
        result = db.queryData(query_str)
        points = result.get_points(tags={'user': str(user_id)})
      
        reply_text = ''
        for i, point in enumerate(points):
            time = point['time']
            event_ = point['event']
            money = point['money']
            reply_text += f'[{i}] -> [{time}] : {event_}   {money}\n'

        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=reply_text
            )
        )
    elif re.match(my_event[2], case_):
   
        if len(recieve_message)!=4:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Command Wrong!"
                )
            )

        event_ = recieve_message[1]
        op = recieve_message[2]
        money = int(recieve_message[3])
        if op == '-':
            money *= -1

        db.queryData(f"select * into tmp from accounting_items WHERE event!=\'{event_}\' and  money!={money}  group by *")
        db.queryData("drop measurement accounting_items")
        db.queryData("select * into accounting_items from tmp group by *")
        db.queryData("drop measurement tmp")
        
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Delete success!'
            )
        )
    elif re.match(my_event[3], case_):
        if len(recieve_message)!=2:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Command Wrong!"
                )
            )

        duration=recieve_message[1]
        que=f'select * from accounting_items where time > now()-{duration}'
        res=db.queryData(que)
        user_id = event.source.user_id
        points = res.get_points(tags={'user': str(user_id)})
        
        total=0
        for i, point in enumerate(points):
            money = point['money']
            total+=money

        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=f"結算金額={total}"
            )
        )


    else:
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=str(event.message.text)
            )
        )

# Line Sticker Class
class My_Sticker:
    def __init__(self, p_id: str, s_id: str):
        self.type = 'sticker'
        self.packageID = p_id
        self.stickerID = s_id

'''
See more about Line Sticker, references below
> Line Developer Message API, https://developers.line.biz/en/reference/messaging-api/#sticker-message
> Line Bot Free Stickers, https://developers.line.biz/en/docs/messaging-api/sticker-list/
'''
# Add stickers into my_sticker list
my_sticker = [My_Sticker(p_id='446', s_id='1995'), My_Sticker(p_id='446', s_id='2012'),
     My_Sticker(p_id='446', s_id='2024'), My_Sticker(p_id='446', s_id='2027'),
     My_Sticker(p_id='789', s_id='10857'), My_Sticker(p_id='789', s_id='10877'),
     My_Sticker(p_id='789', s_id='10881'), My_Sticker(p_id='789', s_id='10885'),
     ]

# Line Sticker Event
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    # Random choice a sticker from my_sticker list
    ran_sticker = random.choice(my_sticker)
    # Reply Sticker Message
    My_LineBotAPI.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id= ran_sticker.packageID,
            sticker_id= ran_sticker.stickerID
        )
    )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', reload=True, host='0.0.0.0', port=8787)
