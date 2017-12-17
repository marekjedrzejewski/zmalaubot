#!/usr/bin/python3

# ₿Ξ
import sys
import time
from matrix_client.client import MatrixClient
from engines import CryptoEngine

if len(sys.argv) != 4:
    print("USAGE: ./zmalaubot.py username password room")
    sys.exit(1)

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]
ROOMNAME = sys.argv[3]


class ZmalauBot():
    def __init__(self, username, password, roomname):
        # connect to room
        self.crypto = CryptoEngine()
        self.client = MatrixClient("http://matrix.org")
        self.token = self.client.login_with_password(username=username,
                                                     password=password)
        self.room = self.client.join_room(roomname)

        # add bot reactions
        self.room.add_listener(self.on_message)
        self.client.start_listener_thread()

        self.room.send_text('Dzień dobry')

    def default_response(self, message):
        return self.crypto.analyze_message_and_prepare_response(message)

    def on_message(self, room, event):
        if event['type'] == "m.room.message":
            if USERNAME in event['sender']:
                return
            if event['content']['msgtype'] == "m.text":
                message = event['content']['body']
                m = message.lower()
                if 'zmalau' in m or 'urus' in m:
                    if any([word in m for word in self.crypto.trigger_words]):
                        response = self.crypto.analyze_message_and_prepare_response(m)
                    else:
                        response = self.default_response(m)
                    self.room.send_text(response)


ZmalauBot(USERNAME, PASSWORD, ROOMNAME)
while True:
    time.sleep(1)
