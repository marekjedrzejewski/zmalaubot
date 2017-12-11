#!/bin/python3

from matrix_client.client import MatrixClient
import sys

if len(sys.argv) != 4:
    print("USAGE: ./zmalaubot.py username password room")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
roomname = sys.argv[3]


client = MatrixClient("http://matrix.org")

token = client.login_with_password(username=username, password=password)

room = client.join_room(roomname)


def on_message(room, event):
    if event['type'] == "m.room.message":
        if username in event['sender']:
            return
        if event['content']['msgtype'] == "m.text":
            message = event['content']['body']
            if 'zmalau' in message:
                room.send_text('urus')
            if 'urus' in message:
                room.send_text('zmalau')


room.add_listener(on_message)
client.start_listener_thread()

while True:
    msg = input()
    if msg == "/quit":
        break
    else:
        room.send_text(msg)
