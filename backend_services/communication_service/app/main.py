from data_classes import MessagePayload, Room, UserWebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

rooms: dict[str, Room] = {}
"""Dict where keys are the room-ID, values are the room's info."""


@app.websocket("/communication/{room_id}/{user_id}")
async def join_communication_channel(websocket: WebSocket, room_id: str, user_id: str):
    global rooms

    await websocket.accept()

    # If the room_id doesn't exist in the dict yet, create it.
    if room_id not in rooms:
        rooms[room_id] = Room()
    room = rooms[room_id]

    user_websocket = UserWebSocket(
        user_id=user_id, websocket=websocket)

    if room.is_full():
        await websocket.send_json({
            "event": "room-full",
            "message": "The room is already full. You cannot join at the moment."
        })
        await websocket.close()
        return

    room.clients[user_websocket.user_id] = user_websocket

    chat_messages = room.chat_room.get_messages()
    for sender_id, message, msg_type in chat_messages:
        if msg_type == 'message':
            await websocket.send_json({
                "event": "receive-message",
                "sender": sender_id,
                "message": message,
                "msg_type": msg_type
            })
        elif msg_type == 'join':
            await websocket.send_json({
                "event": "join-room",
                "sender": sender_id,
                "message": '',
                "msg_type": msg_type
            })
        elif msg_type == 'leave':
            await websocket.send_json({
                "event": "leave-room",
                "sender": sender_id,
                "message": '',
                "msg_type": msg_type
            })

    try:
        while True:
            data: MessagePayload = await websocket.receive_json()
            event = data.get("event")
            if event == "send-message":
                message = data.get("message")
                sender = data.get("sender")
                room.chat_room.add_message(
                    sender_id=sender, message=message, msg_type='message')
                for client_id, client in room.clients.items():
                    if client_id != user_websocket.user_id:  # Exclude the sender
                        await client.websocket.send_json({
                            "event": "receive-message",
                            "sender": sender,
                            "message": message
                        })
            elif event == 'join-room':
                sender = data.get("sender")
                room.chat_room.add_message(
                    sender_id=sender, message='', msg_type='join')
                for client_id, client in room.clients.items():
                    if client_id != user_websocket.user_id:  # Exclude the sender
                        await client.websocket.send_json({
                            "event": "join-room",
                            "sender": sender,
                        })
            elif event == 'leave-room':
                sender = data.get("sender")
                room.chat_room.add_message(
                    sender_id=sender, message='', msg_type='leave')
                for client_id, client in room.clients.items():
                    if client_id != user_websocket.user_id:  # Exclude the sender
                        await client.websocket.send_json({
                            "event": "leave-room",
                            "sender": sender,
                        })

    except WebSocketDisconnect:
        if user_websocket.user_id in room.clients:
            for client_id, client in room.clients.items():
                if client_id != user_websocket.user_id:
                    await client.websocket.send_json({
                        "event": "leave-room",
                        "sender": user_websocket.user_id,
                    })
            del room.clients[user_websocket.user_id]
