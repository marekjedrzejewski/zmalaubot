#!/usr/bin/python3

# ₿Ξ
from urllib import request
import json
from matrix_client.client import MatrixClient
import sys
import time

SUPPORTED_FIAT = ['USD', 'EUR', 'PLN']
DEFAULT_FIAT = 'USD'
SUPPORTED_CRYPTO = ['BTC', 'ETH']
DEFAULT_CRYPTO = 'BTC'

if len(sys.argv) != 4:
    print("USAGE: ./zmalaubot.py username password room")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
roomname = sys.argv[3]


class ZmalauBot():
    def __init__(self, username, password, roomname):
        # init all cryptos on start
        self.last_price = {}
        for crypto in SUPPORTED_CRYPTO:
            self.last_price[crypto] = self.check_current_price(crypto)

        # connect to room
        self.client = MatrixClient("http://matrix.org")
        self.token = self.client.login_with_password(username=username,
                                                     password=password)
        self.room = self.client.join_room(roomname)

        # add bot reactions
        self.room.add_listener(self.on_message)
        self.client.start_listener_thread()

    @staticmethod
    def check_current_price(crypto_symbol):
        return json.load(request.urlopen("https://min-api.cryptocompare.com/"
                                         f"data/price?fsym={crypto_symbol}"
                                         f"&tsyms={','.join(SUPPORTED_FIAT)}"))

    def on_message(self, room, event):
        if event['type'] == "m.room.message":
            if username in event['sender']:
                return
            if event['content']['msgtype'] == "m.text":
                message = event['content']['body']
                m = message.lower()
                if 'zmalau' in m or 'urus' in m:
                    self.analyze_message_and_respond(message)

    def analyze_message_and_respond(self, message):
        m = message.upper()
        used_crypto = [c for c in SUPPORTED_CRYPTO if c in m]
        used_fiat = [f for f in SUPPORTED_FIAT if f in m]

        if not used_crypto:
            used_crypto = [DEFAULT_CRYPTO]
        if not used_fiat:
            used_fiat = [DEFAULT_FIAT]

        fiat = used_fiat[0]

        for crypto in used_crypto:
            current_price = self.check_current_price(crypto)
            change = current_price[fiat] / self.last_price[crypto][fiat] - 1
            if change > 0:
                status = f'{crypto} urus.'
            elif change < 0:
                status = f'{crypto} zmalau.'
            else:
                status = f'{crypto} stoi.'

            change *= 100
            if change != 0:
                status += f' zmiana: {change:.4f}%'
            for fiat in used_fiat:
                status += '\n1 {crypto} = {amount} {currency} '.format(crypto=crypto,
                                                                       amount=current_price[fiat],
                                                                       currency=fiat)
                self.last_price[crypto] = current_price
            self.room.send_text(status)


zmalaubot = ZmalauBot(username, password, roomname)
while True:
    time.sleep(1)
