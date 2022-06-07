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
import sys, threading
sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**27)  # new thread will get stack of such size


import tweepy

client = tweepy.Client(consumer_key='',
                       consumer_secret='',
                       access_token='',
                       access_token_secret='')



EXA = 10**18


def getlog():
    craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1',timeout=20)
    logdata = craft_log.text
    json_logdata = json.loads(logdata)
    latesttx = json_logdata[0]
    global txhash
    txhash = latesttx["transaction_hash"]
    indexed = latesttx["indexed"]
    json_indexed = json.loads(indexed)
    global operator
    operator = json_indexed[1]
    global seller
    seller = json_indexed[2]
    global reciever
    reciever = json_indexed[3]
    global sale
    
    
    if operator == "cx9c4698411c6d9a780f605685153431dcda04609f":
        sale = 1
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time + " ### NFT SOLD ###")
        print("From: ", seller)
        print("To: ", reciever)
        print("TxHash: ", txhash)
        print("Operator: " + operator) 
        
    else:
         sale = 0
    
    if sale == 1: 
        gettxresult()
        
    else:
           print("Operator is not craft contract")
           op_not_craft()


    
    
    
def gettxresult():
    txresult = icon_service.get_transaction_result(txhash)
    result3 = txresult["eventLogs"][0]
    global status
    status = result3["indexed"][0]
    print(status)
    if status != "ICXTransfer(Address,Address,int)":
        status_nosale()
    else:
        result2 = txresult["eventLogs"][4]
        hexamount = result3["indexed"][3]
        exaamount = int(hexamount, 16)
        global amount
        amount = exaamount / EXA
        stramount = str(amount)
        print("Amount: " + stramount)
        hextokenid = result2["data"][0]
        global tokenid
        tokenid = int(hextokenid, 16)
        global strtokenid
        strtokenid = str(tokenid)
        print("Token ID: " + strtokenid)
        global url
        url = "https://craft.network/nft/cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa:" + strtokenid
        tweet()


def status_nosale():
    print("Last TX was not a direct purchase")
    time.sleep(5)
    global status
    while status != "ICXTransfer(Address,Address,int)":
        print("Gettning new data")
        s_craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1',timeout=20)
        s_logdata = s_craft_log.text
        s_json_logdata = json.loads(s_logdata)
        s_latesttx = s_json_logdata[0]
        global txhash
        txhash = s_latesttx["transaction_hash"]
        txresult = icon_service.get_transaction_result(txhash)
        s_result3 = txresult["eventLogs"][0]
        status = s_result3["indexed"][0]
        print("Status: " + status)
        time.sleep(5)
    else:
        print("Status:" + status)
        getlog()
    
    
def op_not_craft():
    global operator
    global sale
    while operator != "cx9c4698411c6d9a780f605685153431dcda04609f":
        d_craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1',timeout=20)
        d_logdata = d_craft_log.text
        d_json_logdata = json.loads(d_logdata)
        d_latesttx = d_json_logdata[0]          
        d_indexed = d_latesttx["indexed"]
        d_json_indexed = json.loads(d_indexed)
        operator = d_json_indexed[1]
        strsale = str(sale)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print(current_time)
        print("######################################")
        print("Sale var: " + strsale)
        print("Operator is not craft contract")
        print("Operator: " + operator)
        print("######################################")
      
        time.sleep(10)
    else:
        sale = 1
        getlog()

def check_old():
    try:
        craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1',timeout=20)
        logdata = craft_log.text
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
        while newtxhash == txhash:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")


            
            print(current_time + " Nothing New")
            new_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1',timeout=20)
            newlogdata = new_log.text
            json_newlogdata = json.loads(newlogdata)
            newlatesttx = json_newlogdata[0]
            newtxhash = newlatesttx["transaction_hash"]
            print("last tx: " + newtxhash)
            
            time.sleep(10)
        else:
            getlog()

def tweet():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    stramount = str(amount)
    text = "Claw: " + strtokenid + " was just sold for " + stramount + " ICX" + "\n" + url
    response = client.create_tweet(text=text)
    print(current_time + " Tweet: " + f"https://twitter.com/clawnftsales/status/{response.data['id']}")
    
    check_old()


print("Starting Bot")
getlog()
