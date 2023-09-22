from fastapi import FastAPI, HTTPException,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading

# create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

queue = []

class User:
    def __init__(self, user_id, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global queue

    await websocket.accept()

    try:
        # Receive message from client
        message = await websocket.receive_text()

        request =  json.loads(message)
        detail = request["detail"]
        user_id = detail["user_id"]

        user = User(user_id, websocket)
        queue.append(user)

    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)

def check_for_matches():
    global queue
    while True:
        if len(queue) >= 2:
            user1 = queue.pop(0)
            user2 = queue.pop(0)
            notify_users_of_match(user1, user2)

def notify_users_of_match(user1: User, user2: User):
    user1.websocket.send_text(f"You have matched with {user2.user_id}")
    user2.websocket.send_text(f"You have matched with {user1.user_id}")

matching_thread = threading.Thread(target=check_for_matches)
matching_thread.start()