#!/usr/bin/python3

# ₿Ξ
import sys
import time
from urllib import request
import json
from matrix_client.client import MatrixClient

SUPPORTED_FIAT = ['USD', 'EUR', 'PLN']
DEFAULT_FIAT = 'USD'
SUPPORTED_CRYPTO = ['BTC', 'ETH', 'LTC', 'IOT', 'DOGE', 'BCH', 
                    'XRP', 'DASH', 'XMR', 'EOS', 'NEO', 'OMG',
                    'LSK', 'ZEC', 'NXT', 'ARDR', 'GNT' ]
DEFAULT_CRYPTO = 'BTC'

if len(sys.argv) != 4:
    print("USAGE: ./zmalaubot.py username password room")
    sys.exit(1)

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]
ROOMNAME = sys.argv[3]


class ZmalauBot():
    def __init__(self, username, password, roomname):
        # init all cryptos on start
        self.last_price = {}
        self.last_price = self.check_current_price_for_all_supported_cryptos()

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
                                         f"&tsyms={','.join(SUPPORTED_FIAT)}"
                                         ))
                                        
    @staticmethod
    def check_current_price_for_all_supported_cryptos():
        return json.load(request.urlopen("https://min-api.cryptocompare.com/"
                                         f"data/pricemulti?fsyms={','.join(SUPPORTED_CRYPTO)}"
                                         f"&tsyms={','.join(SUPPORTED_FIAT)}"
                                         ))

    def on_message(self, room, event):
        if event['type'] == "m.room.message":
            if USERNAME in event['sender']:
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


ZmalauBot(USERNAME, PASSWORD, ROOMNAME)
while True:
    time.sleep(1)
