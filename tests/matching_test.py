import asyncio
import websockets
import json

async def send_message():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        # message = {
        #     'service': 'matching-service',
        #     'message': {
        #         'user_id': '123',
        #         'complexity': 'easy'
        #     }
        # }
        message = {
            "service": "matching-service",
            "message": {
                "user_id": "1234",
                "complexity": "easy"
            }
        }
        await ws.send(json.dumps(message))
        response = await ws.recv()
        response = json.loads(response)
        print("Response: ", response)

if __name__ == "__main__":
    asyncio.run(send_message())