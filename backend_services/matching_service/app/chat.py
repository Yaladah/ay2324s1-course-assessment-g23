import json
from fastapi import WebSocket
import aio_pika
import asyncio
import logging
from matching_util import set_message_received

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def send_text_to_room(sender_id: str, room_id: str, text: str):
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/%2F")
        channel = await connection.channel()

        message = {
            "action": "chat",
            "sender_id": sender_id,
            "room_id": room_id,
            "text": text
        }
        logger.info(f"Chat to be sent: {message}")
        await channel.declare_queue("room_queue")
        data = json.dumps(message)
        await channel.default_exchange.publish(
            aio_pika.Message(body=data.encode()),
            routing_key="room_queue"
        )
        return ''
    except Exception as e:
        logger.info(e)


async def wait_for_chat(user_id: str, websocket: WebSocket):
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/%2F")
        channel = await connection.channel()

        receive_chat_queue_name = f"{user_id}_q"
        queue = await channel.declare_queue(receive_chat_queue_name)
        consumer_tag = None

        async def on_response(message):
            async with message.process():
                data = json.loads(message.body)
                action = data["action"]
                if action == "receive_chat":
                    sender_id = data["sender_id"]
                    text = data["text"]
                    reply = {
                        "sender_id": sender_id,
                        "text": text
                    }
                    await websocket.send_text(json.dumps(reply))
                    set_message_received(user_id)

        logger.info(f"{user_id} waiting to receive chats")
        consumer_tag = await queue.consume(on_response)

    except fastapi.websockets.WebSocketDisconnect:
        logger.info("WS disconnected")
        if consumer_tag is not None:
            await queue.cancel(consumer_tag)
    except Exception as e:
        logger.info(e)
