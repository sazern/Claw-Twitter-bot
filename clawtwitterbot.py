import requests
import json
import time
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from datetime import datetime
import sys, threading
sys.setrecursionlimit(10**7) # max depth of recursion
threading.stack_size(2**27)  # new thread will get stack of such size
import tweepy
icon_service = IconService(HTTPProvider("https://ctz.solidwallet.io/api/v3"))

#Insert twitter auth credentials
client = tweepy.Client(consumer_key='',
                       consumer_secret='',
                       access_token='',
                       access_token_secret='')



EXA = 10**18

#Gets the latest transaction to the Claw contract address with method "TransferSingle" from ICON API.
def getlog():
    try:
        craft_log = requests.get('https://tracker.icon.community/api/v1/logs?address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1', timeout=(10, 10))
         
    except:
        time.sleep(20)
        getlog()
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
    
    #Making sure the Operator is Craft contract to be sure its sold on craft network
    if operator == "cx9c4698411c6d9a780f605685153431dcda04609f":
        sale = 1      
     
        
    else:
         sale = 0
    # If its a sale with craft contract as operator, lets continue get the TX details
    if sale == 1: 
        gettxresult()
        
    else:
           
        op_not_craft()


    
    
# Lets get the TX details to get tokenID and the Value that it was sold for 
def gettxresult():
    
    txresult = icon_service.get_transaction_result(txhash)
    result3 = txresult["eventLogs"][0]
    global status
    status = result3["indexed"][0]
    #Checks if it was a direct sale or a auction
    if status != "ICXTransfer(Address,Address,int)":
        status_nosale()
    else:
        
        result2 = txresult["eventLogs"][1]
        royhexamount = result2["indexed"][3]
        roydec = int(royhexamount, 16) / EXA
        global roystramount
        roystramount= str(roydec)

        royadress = "hx5533bf0fdfcf7d90c703b7a4000e9c9dd3245066"
        roybalance = icon_service.get_balance(royadress) / EXA
        global strbalance
        strbalance = str(roybalance)

        result2 = txresult["eventLogs"][5]
        hexamount = result3["indexed"][3]
        exaamount = int(hexamount, 16)
        global amount
        amount = exaamount / EXA
        stramount = str(amount)
        try:
            hextokenid = result2["data"][0]
            global tokenid
            tokenid = int(hextokenid, 16)
            global strtokenid
            strtokenid = str(tokenid)
        except:
            time.sleep(20)
            gettxresult()

#        rarity_url = "https://api.rarityhunter.network/v1/api/nft?contractAddress=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&tokenId=" + strtokenid
#        rarity_apiurl = rarity_url
#        rarity_api = requests.get(rarity_apiurl)
#        rarity_data = rarity_api.text
#        json_rarity = json.loads(rarity_data)
#        rarity_rank = json_rarity["data"]["rank"]
#        global strrank
#        strrank = str(rarity_rank)
# 	rank = 0
#	strrank = str(rank)
       
        global url
        url = "https://craft.network/nft/cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa:" + strtokenid
        
        #Lets send a tweet about it!
        tweet()

# Checks the api for new sale if it wasnt a direct purchase
def status_nosale():
    
    time.sleep(5)
    global status
    while status != "ICXTransfer(Address,Address,int)":
        
        try:
            s_craft_log = requests.get('https://tracker.icon.community/api/v1/logs?address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1', timeout=(10, 10))
        except:
            time.sleep(20)
            status_nosale()
        s_logdata = s_craft_log.text
        s_json_logdata = json.loads(s_logdata)
        s_latesttx = s_json_logdata[0]
        global txhash
        txhash = s_latesttx["transaction_hash"]
        txresult = icon_service.get_transaction_result(txhash)
        s_result3 = txresult["eventLogs"][0]
        status = s_result3["indexed"][0]
        
        
        time.sleep(20)
        
    else:
        print("Status:" + status)
        getlog()
    
# Checks the api again untill Operator is craft contract    
def op_not_craft():
    global operator
    global sale
    while operator != "cx9c4698411c6d9a780f605685153431dcda04609f":
        try:
            d_craft_log = requests.get('https://tracker.icon.community/api/v1/logs?address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1', timeout=(10, 10))
        except:
            time.sleep(20)
            op_not_craft()
        d_logdata = d_craft_log.text
        d_json_logdata = json.loads(d_logdata)
        d_latesttx = d_json_logdata[0]          
        d_indexed = d_latesttx["indexed"]
        d_json_indexed = json.loads(d_indexed)
        operator = d_json_indexed[1]
        strsale = str(sale)
      
      
        
        time.sleep(20)
    else:
        sale = 1
        getlog()

# Checks the latest transaction for a new sale, If the last tx is the same, then it checks it again 
def check_old():
    
    try:
        craft_log = requests.get('https://tracker.icon.community/api/v1/logs?address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1', timeout=(10, 10))
        logdata = craft_log.text
        json_logdata = json.loads(logdata)
    except:
        time.sleep(20)
        check_old()
    latesttx = json_logdata[0]
    newtxhash = latesttx["transaction_hash"]
    
    while newtxhash == txhash:  
                
        try:
            new_log = requests.get('https://tracker.icon.community/api/v1/logs?address=cx45cf0c108c3df650b1c28d9e2fdc8b4d068cb2fa&method=TransferSingle&limit=1', timeout=(10, 10))
        except:
            time.sleep(20)
            check_old()
        newlogdata = new_log.text
        json_newlogdata = json.loads(newlogdata)
        newlatesttx = json_newlogdata[0]
        newtxhash = newlatesttx["transaction_hash"]
            
            
        
        time.sleep(5)
    else:
        getlog()
# Tweets the sale
def tweet():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    stramount = str(amount)
    text = "Claw: " + strtokenid + " was just sold for " + stramount + " $ICX" + " and " + roystramount + " $ICX" + " in royalties" + "\n" + "\n" + "Current balance of Claw Royalty wallet is: " + strbalance + " ICX" + "\n" + url

    try:
        response = client.create_tweet(text=text)
        print(current_time + " Tweet: " + f"https://twitter.com/clawnftsales/status/{response.data['id']}")
        
        
    
        check_old()
    except:
        print("Dublicated tweet, Checking for new TX")
        check_old()


print("Starting Bot")
getlog()


