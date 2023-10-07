from fastapi import FastAPI, HTTPException,  WebSocket
import json
from fastapi.middleware.cors import CORSMiddleware
import threading

from matching_util import User
from queue_manager import consume_queue, check_for_matches, send_user_to_queue

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

@app.websocket("/ws/matching")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive message from client
        message = await websocket.receive_text()
        print("Message: ", message)
        request =  json.loads(message)
        detail = request["message"]
        user_id = detail["user_id"]
        complexity = detail["complexity"]
        
        # await websocket.send_text(json.dumps(request))

        send_user_to_queue(user_id, complexity)

        # consume_queue(f'{complexity}_queue', websocket)
        
        await websocket.close()

    except HTTPException as http_exc:
        await websocket.send_text(http_exc.detail)

matching_thread = threading.Thread(target=check_for_matches)
matching_thread.start()