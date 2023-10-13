import pika
import json
from fastapi import WebSocket
import websockets
import aio_pika

from matching_util import User, message_received

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def send_user_to_queue(user_id, complexity):
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/%2F")
        channel = await connection.channel()

        queue_name = f'{complexity}_queue'
        await channel.declare_queue(queue_name)
        message = {
            "user_id": f"{user_id}",
            "complexity": f"{complexity}"
        }
        data = json.dumps(message)
        logger.info(f"{user_id} sent to queue")
        await channel.default_exchange.publish(
            aio_pika.Message(body=data.encode()),
            routing_key=queue_name,
        )
        
        return ''
    except Exception as e:
        logger.info(f"Error occurred: {str(e)}")
        return None
    
async def listen_for_server_replies(user_id: str, websocket: WebSocket):
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/%2F")
        channel = await connection.channel()

        # Declare a unique reply queue for this listener
        reply_queue_name = f'{user_id}_q'
        queue = await channel.declare_queue(reply_queue_name)
        async def on_response(message):
            async with message.process():
                response_data = json.loads(message.body)
                logger.info(f"response_data: {response_data}")
                user1 = response_data["user1"]
                user2 = response_data["user2"]
                user1_id = user1["user_id"]
                user2_id = user2["user_id"]
                if user1_id == user_id:
                    id = user2_id
                else:
                    id = user1_id
                logger.info(f"{id} has matched")
                message = f"You have matched with {id}!"
                await websocket.send_text(json.dumps(message))
                message_received.set()

        logger.info(f"{user_id} waiting for response...")
        await queue.consume(on_response)
    except Exception as e:
        logger.info(f"Error occurred: {str(e)}")