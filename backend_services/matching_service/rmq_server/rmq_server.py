import logging
import sys
import os
import json
import asyncio
import time
import aio_pika

# create queues for each complexity
complexity_queues = {
    'easy_queue': [],
    'medium_queue': [],
    'hard_queue': []
}

lock = asyncio.Lock()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure logging to write to stdout
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
                user_data = json.loads(message.body)
                user_id = user_data["user_id"]
                complexity = user_data["complexity"]
                queue_name = f'{complexity}_queue'
                action = user_data["action"]
                logger.info(f"{user_data} received")
                async with lock:
                    if action == "queue":
                        curr_queue = complexity_queues[queue_name]
                        if user_id not in curr_queue:
                            curr_queue.append(user_id)
                        logger.info(f"Current queue: {curr_queue}")
                        if len(curr_queue) >= 2:
                            user1_id = curr_queue.pop(0)
                            user2_id = curr_queue.pop(0)
                            reply = {
                                "user1": user1_id,
                                "user2": user2_id
                            }
                            logger.info(f"Reply: {reply}")
                            await channel.declare_queue(f'{user1_id}_q')
                            await channel.declare_queue(f'{user2_id}_q')
                            await channel.default_exchange.publish(
                                aio_pika.Message(
                                    body=json.dumps(reply).encode(),
                                ),
                                routing_key=f'{user1_id}_q',
                            )
                            await channel.default_exchange.publish(
                                aio_pika.Message(
                                    body=json.dumps(reply).encode(),
                                ),
                                routing_key=f'{user2_id}_q',
                            )
                        else:
                            await asyncio.sleep(1)
                    elif action == "cancel":
                        curr_queue = complexity_queues[queue_name]
                        logger.info(f"Queue before delete: {curr_queue}")
                        if user_id in curr_queue:
                            curr_queue.remove(user_id)
                        logger.info(f"Queue after delete: {curr_queue}")

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
