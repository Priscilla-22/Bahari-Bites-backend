# server/chat.py
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from .models import User
from .app import socketio
import os


@socketio.on("connect")
def handle_connect():
    emit("message", {"msg": "Connected to chat server"})


@socketio.on("disconnect")
def handle_disconnect():
    emit("message", {"msg": "Disconnected from chat server"})


@socketio.on("join")
def handle_join(data):
    room = data["room"]
    join_room(room)
    emit("message", {"msg": f'{data["username"]} has joined the room.'}, room=room)


@socketio.on("leave")
def handle_leave(data):
    room = data["room"]
    leave_room(room)
    emit("message", {"msg": f'{data["username"]} has left the room.'}, room=room)


@socketio.on("send_message")
def handle_send_message(data):
    room = data["room"]
    emit("message", {"msg": data["msg"], "username": data["username"]}, room=room)
