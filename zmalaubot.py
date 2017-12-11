#!/bin/python3

from urllib import request
import json
from matrix_client.client import MatrixClient
import sys

if len(sys.argv) != 4:
    print("USAGE: ./zmalaubot.py username password room")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
roomname = sys.argv[3]

def check_current_price():
    return json.load(request.urlopen("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR"))

last_price = check_current_price()

client = MatrixClient("http://matrix.org")

token = client.login_with_password(username=username, password=password)

room = client.join_room(roomname)


def on_message(room, event):
    global last_price
    if event['type'] == "m.room.message":
        if username in event['sender']:
            return
        if event['content']['msgtype'] == "m.text":
            message = event['content']['body']
            if 'zmalau' in message or 'urus' in message:
                current_price = check_current_price()
                change = current_price['USD'] / last_price['USD'] - 1
                if change > 0:
                    status = 'urus'
                elif current_price['USD'] < last_price['USD']:
                    status = 'zmalau'
                else:
                    status = 'stoi'
                room.send_text('{status}. zmiana: {change:.4f}%, cena: {usd}USD'
                        .format(status=status,
                                change=change*100,
                                usd=current_price['USD']))
                last_price = current_price


room.add_listener(on_message)
client.start_listener_thread()

while True:
    msg = input()
    if msg == "/quit":
        break
    else:
        room.send_text(msg)
