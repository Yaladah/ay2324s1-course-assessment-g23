from typing import Optional
from fastapi import FastAPI, HTTPException, Query,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading
import websockets
from matching_util import User, message_received
from matching import send_user_to_queue, listen_for_server_replies
import asyncio

# create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app = FastAPI()

@app.websocket("/ws/matching")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive message from client
        request = await websocket.receive_text()
        message =  json.loads(request)
        user_id = message["user_id"]
        complexity = message["complexity"]

        await send_user_to_queue(user_id, complexity)
        listener_task = asyncio.create_task(listen_for_server_replies(user_id, websocket))
        await message_received.wait()
        # await websocket.close()

    except Exception as e:
        # Log any other exceptions for debugging
        print(f"An error occurred: {e}")

