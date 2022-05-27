import requests
import json
import os
import time
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
import tweepy

icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io/api/v3"))
claw_contract = "cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa"


#LOGIN To twitter
client = tweepy.Client(consumer_key='',
                       consumer_secret='',
                       access_token='',
                       access_token_secret='')



EXA = 10**18

#Get data from icon API of sales where claw contract = score_address
def getlog():
    craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle')
    logdata = craft_log.text
    json_logdata = json.loads(logdata)
    latesttx = json_logdata[0] #latest row of data
    global txhash
    txhash = latesttx["transaction_hash"]
    indexed = latesttx["indexed"]
    json_indexed = json.loads(indexed)
    operator = json_indexed[1]
    global seller
    seller = json_indexed[2]
    global reciever
    reciever = json_indexed[3]
    
    if operator == "cx9c4698411c6d9a780f605685153431dcda04609f": #Making sure its from craft contract == sale
        sale = 1
    else:
         sale = 0
    
    if sale == 1:
        print("### NFT SOLD ###")
        print("From: ", seller)
        print("To: ", reciever)
        print("TxHash: ", txhash)
        
        gettxresult()
        
    else:
        getlog()


    
    
    #Get TX data of the latest sale
def gettxresult():
    txresult = icon_service.get_transaction_result(txhash)
    result2 = txresult["eventLogs"][4]
    result3 = txresult["eventLogs"][0]
    hexamount = result3["indexed"][3] #Price not including fees
    exaamount = int(hexamount, 16)
    global amount
    amount = exaamount / EXA
    print("Amount: ", amount, " ICX")
    hextokenid = result2["data"][0] #Gets tokenid of NFT sold
    global tokenid
    tokenid = int(hextokenid, 16)
    global strtokenid
    strtokenid = str(tokenid)
    print("TokenID: ", tokenid)
    global url
    url = "https://craft.network/nft/cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa:" + strtokenid
    print(url)
    tweet()
    

#Checks TX Hash to find out if there was a new sale
def check_old():
    craft_log = requests.get('https://tracker.icon.community/api/v1/logs?score_address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle')
    logdata = craft_log.text
    json_logdata = json.loads(logdata)
    latesttx = json_logdata[0]
    newtxhash = latesttx["transaction_hash"]
    if newtxhash == txhash:
        

        time.sleep(60)
        check_old()
    else:
        getlog()

    
#Tweets the sale
def tweet():
    stramount = str(amount)
    text = "Claw: " + strtokenid + " was just sold for " + stramount + " ICX" + "\n" + url
    
    response = client.create_tweet(text=text)

    print(response)
    check_old()

getlog()

