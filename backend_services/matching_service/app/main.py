from fastapi import FastAPI, WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import logging

from matching_util import add_event
from matching import send_user_to_queue, wait_for_match, remove_user_from_queue
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
    try:
        # Receive message from client
        request = await websocket.receive_text()
        message = json.loads(request)
        user_id = message["user_id"]
        complexity = message["complexity"]
        action = message["action"]
        if action == "queue":
            user_event = asyncio.Event()
            add_event(user_id, user_event)
            logger.info(f"Sending {user_id} to queue")
            await send_user_to_queue(user_id, complexity)
            listener_task = asyncio.create_task(
                wait_for_match(user_id, complexity, websocket))
            await user_event.wait()
        elif action == "cancel":
            await remove_user_from_queue(user_id, complexity)
        logger.info(f"Closing websocket for {user_id}")
    except Exception as e:
        # Log any other exceptions for debugging
        print(f"An error occurred: {e}")
    finally:

        await websocket.close()
