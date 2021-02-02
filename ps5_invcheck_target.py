import requests
import json
import os
import time

def playsound(location, quantity):
    os.system('say "{} {}"'.format(location, quantity))

 
url = "https://api.target.com/fulfillment_aggregator/v1/fiats/81114595?key=ff457966e64d5e877fdbad070f276d18ecec4a01&nearby=92026&limit=20&requested_quantity=1&radius=500&fulfillment_test_mode=grocery_opu_team_member_test"

payload={}
headers = {
'authority': 'api.target.com',
'accept': 'application/json',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
'origin': 'https://www.target.com',
'sec-fetch-site': 'same-site',
'sec-fetch-mode': 'cors',
'sec-fetch-dest': 'empty',
'referer': 'https://www.target.com/c/playstation-5-video-games/-/N-hj96d?lnk=snav_rd_playstation_5',
'accept-language': 'en-US,en;q=0.9'
}

response = requests.request("GET", url, headers=headers, data=payload)

products = response.json()['products']
locations = products[0]['locations']

# Show locations and availibility on startup for testing purposes
for location in locations:
    print(location["store_name"], location['location_available_to_promise_quantity'])


def checkTarget(): 
    #print("Checking availibility")
    for location in locations:
        quantity = int(location['location_available_to_promise_quantity'])
        if quantity > 0:
            playsound(location["store_name"], str(quantity))
            return 1
        return 0