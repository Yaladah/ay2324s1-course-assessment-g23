from typing import Optional
from fastapi import FastAPI, HTTPException, Query,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading
import websockets
from matching_util import User
from matching import send_user_to_queue, listen_for_server_replies
import asyncio
from rmq_server import main
# from queue_manager import consume_queue, check_for_matches, send_user_to_queue

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
        user = User(user_id=user_id, complexity=complexity, websocket=websocket)
        # await websocket.send_text(json.dumps(user))

        await send_user_to_queue(user)
        # # consume_queue(f'{complexity}_queue', websocket)
        # listener_thread = await threading.Thread(target=listen_for_server_replies)
        # listener_thread.start()
        # listener_thread.join()
        listener_task = asyncio.create_task(listen_for_server_replies(user_id))
        await listener_task
        websocket.close()

    except websockets.exceptions.ConnectionClosedError as conn_closed_exc:
        # Handle WebSocket connection closed errors
        print(f"WebSocket connection closed: {conn_closed_exc}")
    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)
    except Exception as e:
        # Log any other exceptions for debugging
        print(f"An error occurred: {e}")

