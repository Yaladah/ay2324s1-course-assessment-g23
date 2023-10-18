import aio_pika
import time
import logging
import asyncio
import json
import os
import sys

lock = asyncio.Lock()

# create chat rooms
rooms = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def create_room(room_id):
    if room_id not in rooms:
        rooms[room_id] = []


def add_user_to_room(room_id, user_id):
    if room_id in rooms:
        rooms[room_id].append(user_id)
    else:
        # Room doesn't exist, so you can choose to handle this case accordingly
        logger.info(f"Room {room_id} does not exist")


async def main():
    is_connected = False

    while not is_connected:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/%2F")
            channel = await connection.channel()
            is_connected = True
        except:
            time.sleep(2)
            is_connected = False
            logger.info("Retrying")

    try:
        async def callback(message):
            async with message.process():
                data = json.loads(message.body)
                action = data["action"]

                if action == "add_to_room":
                    room_id = data["room_id"]
                    user1 = data["user1"]
                    user2 = data["user2"]
                    create_room(room_id)
                    add_user_to_room(room_id, user1)
                    add_user_to_room(room_id, user2)
                    logger.info(f"Current rooms are {rooms}")
                elif action == "chat":
                    room_id = data["room_id"]
                    sender_id = data["sender_id"]
                    text = data["text"]
                    for user_id in rooms[room_id]:
                        if user_id != sender_id:
                            recipient_queue = f"{user_id}_q"
                            await channel.declare_queue(recipient_queue)
                            relayed_message = {
                                "action": "receive_chat",
                                "sender_id": sender_id,
                                "text": text
                            }
                            await channel.default_exchange.publish(
                                aio_pika.Message(
                                    body=json.dumps(relayed_message).encode(),
                                ),
                                routing_key=recipient_queue
                            )
        room_queue = await channel.declare_queue("room_queue")
        logger.info("Room router ready to accept")
        await room_queue.consume(callback)
    except Exception as e:
        logger.info(e)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
