from fastapi import FastAPI, HTTPException,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading

from .matching_util import User
from .queue_manager import queue, check_for_matches

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

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

matching_thread = threading.Thread(target=check_for_matches)
matching_thread.start()