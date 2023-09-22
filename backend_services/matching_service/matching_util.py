from fastapi import WebSocket

class User:
    def __init__(self, user_id, websocket: WebSocket):
        self.user_id = user_id
        self.websocket = websocket