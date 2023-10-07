from fastapi import WebSocket

class User:
    def __init__(self, user_id, complexity, websocket: WebSocket):
        self.user_id = user_id
        self.complexity = complexity
        self.websocket = websocket