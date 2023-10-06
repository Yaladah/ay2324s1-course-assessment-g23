import asyncio
import websockets
import json

async def send_message():
    async with websockets.connect('ws://localhost:8000/ws') as websocket:
        # message = {
        #     'service': 'matching-service',
        #     'message': {
        #         'user_id': '123',
        #         'complexity': 'easy'
        #     }
        # }
        message = {
            'service': 'matching-service',
            'message': {
                'user_id': '1234',
                'complexity': 'easy'
            }
        }
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(response)

if __name__ == "__main__":
    asyncio.run(send_message())
