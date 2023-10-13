from fastapi import WebSocket
import asyncio

class User:
    def __init__(self, user_id, complexity):
        self.user_id = user_id
        self.complexity = complexity
        
message_received = asyncio.Event()
