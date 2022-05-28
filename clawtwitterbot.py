import logging
import gc
import requests
import json
import time
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io/api/v3"))
claw_contract = "cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa"
from datetime import datetime



import tweepy

client = tweepy.Client(consumer_key='',
                       consumer_secret='',
                       access_token='',
                       access_token_secret='')



EXA = 10**18


def getlog():
    craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1')
    logdata = craft_log.text
    json_logdata = json.loads(logdata)
    latesttx = json_logdata[0]
    global txhash
    txhash = latesttx["transaction_hash"]
    indexed = latesttx["indexed"]
    json_indexed = json.loads(indexed)
    operator = json_indexed[1]
    global seller
    seller = json_indexed[2]
    global reciever
    reciever = json_indexed[3]
    
    if operator == "cx9c4698411c6d9a780f605685153431dcda04609f":
        sale = 1
    else:
         sale = 0
    
    if sale == 1:
        
        
        gettxresult()
        
    else:
        getlog()


    
    
    
def gettxresult():
    txresult = icon_service.get_transaction_result(txhash)
    result2 = txresult["eventLogs"][4]
    result3 = txresult["eventLogs"][0]
    hexamount = result3["indexed"][3]
    exaamount = int(hexamount, 16)
    global amount
    amount = exaamount / EXA
    
    hextokenid = result2["data"][0]
    global tokenid
    tokenid = int(hextokenid, 16)
    global strtokenid
    strtokenid = str(tokenid)
    global url
    url = "https://craft.network/nft/cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa:" + strtokenid
    tweet()
    
    


def check_old():
    
    craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1')
    logdata = craft_log.text
    try:
     json_logdata = json.loads(logdata)
    except json.decoder.JSONDecodeError:
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print(current_time + " Error decoding JSON")
        time.sleep(3)
        check_old()
    else:
        latesttx = json_logdata[0]
        newtxhash = latesttx["transaction_hash"]
        if newtxhash == txhash:
            del craft_log
            del logdata
            del json_logdata
            gc.collect()
            
            time.sleep(10)
            check_old()
        else:
            getlog()

def tweet():
    stramount = str(amount)
    text = "Claw: " + strtokenid + " was just sold for " + stramount + " ICX" + "\n" + url
    
    response = client.create_tweet(text=text)
    print(response)
    
    check_old()



getlog()
