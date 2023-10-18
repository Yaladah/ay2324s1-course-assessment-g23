from fastapi import FastAPI, WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import logging

from matching_util import add_event
from matching import send_user_to_queue, wait_for_match, remove_user_from_queue
from chat import send_text_to_room, wait_for_chat
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@app.websocket("/ws/matching")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            # Receive message from client
            request = await websocket.receive_text()
            message = json.loads(request)
            action = message["action"]
            user_id = message["user_id"]
            if action == "queue":
                complexity = message["complexity"]
                user_event = asyncio.Event()
                add_event(user_id, user_event)
                logger.info(f"Sending {user_id} to queue")
                await send_user_to_queue(user_id, complexity)
                listener_task = asyncio.create_task(
                    wait_for_match(user_id, complexity, websocket))
                await user_event.wait()
            elif action == "cancel":
                complexity = message["complexity"]
                await remove_user_from_queue(user_id, complexity)
            elif action == "chat":
                room_id = message["room_id"]
                text = message["text"]
                await send_text_to_room(user_id, room_id, text)
            elif action == "receive_chat":
                chat_event = asyncio.Event()
                add_event(user_id, chat_event)
                wait_for_chat_task = asyncio.create_task(
                    wait_for_chat(user_id, websocket)
                )
                await chat_event.wait()

        except Exception as e:
            # Log any other exceptions for debugging
            print(f"An error occurred: {e}")
