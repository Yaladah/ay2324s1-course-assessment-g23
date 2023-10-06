from typing import Optional
from fastapi import FastAPI, HTTPException, Query,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading
import websockets
from matching_util import User
from queue_manager import consume_queue, check_for_matches, send_user_to_queue

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

@app.websocket("/matching/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive message from client
        message = await websocket.receive_text()
        request =  json.loads(message)
        detail = request["detail"]
        user_id = detail["user_id"]
        complexity = detail["complexity"]

        await websocket.send_text(json.dumps(request))
        websocket.close()
        # send_user_to_queue(user_id, complexity)

        # consume_queue(f'{complexity}_queue')

    except websockets.exceptions.ConnectionClosedError as conn_closed_exc:
        # Handle WebSocket connection closed errors
        print(f"WebSocket connection closed: {conn_closed_exc}")
    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)
    except Exception as e:
        # Log any other exceptions for debugging
        print(f"An error occurred: {e}")

matching_thread = threading.Thread(target=check_for_matches)
matching_thread.start()