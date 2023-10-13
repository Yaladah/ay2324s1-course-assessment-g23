import pika
import sys
import os
import json
import asyncio
import traceback
import time
import aio_pika

# create queues for each complexity
complexity_queues = {
    'easy_queue': asyncio.Queue(),
    'medium_queue': asyncio.Queue(),
    'hard_queue': asyncio.Queue(),
}

lock = asyncio.Lock()

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
                logger.info("Received message")
                user_data = json.loads(message.body)
                user_id = user_data["user_id"]
                complexity = user_data["complexity"]
                queue_name = f'{complexity}_queue'
                logger.info(f"{user_data} received")
                async with lock:
                    curr_queue = complexity_queues[queue_name]
                    logger.info(f"{curr_queue}")
                    await curr_queue.put(user_data)
                    logger.info(f"{curr_queue}")
                    if curr_queue.qsize() >= 2:
                        user1 = await curr_queue.get()
                        user2 = await curr_queue.get()
                        reply = {
                            "user1": user1,
                            "user2": user2
                        }
                        logger.info(f"Reply: {reply}")
                        user1_id = user1["user_id"]
                        user2_id = user2["user_id"]
                        await channel.declare_queue(f'{user1_id}_q')
                        await channel.declare_queue(f'{user2_id}_q')
                        logger.info(f"User1: {user1_id}")
                        logger.info(f"User2: {user2_id}")
                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(reply).encode(),
                            ),
                            routing_key=f'{user1_id}_q',
                        )
                        logger.info("User 1 replied")
                        await channel.default_exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(reply).encode(),
                            ),
                            routing_key=f'{user2_id}_q',
                        )
                        logger.info("User 2 replied")
                    else:
                        await asyncio.sleep(1)

        queue_names = ['easy_queue', 'medium_queue', 'hard_queue']

        for name in queue_names:
            queue = await channel.declare_queue(name)
            logger.info(f"{name} ready to receive")
            await queue.consume(callback)
    except Exception as e:
        logger.info(f"{e}")


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