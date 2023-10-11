import pika
import sys
import os
import json
import asyncio
import traceback
import time

# create queues for each complexity
complexity_queues = {
    'easy_queue': [],
    'medium_queue': [],
    'hard_queue': [],
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

def main():
    is_connected = False
    
    while not is_connected:
        try:
            credentials = pika.PlainCredentials(username='guest', password='guest')
            parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
            connection = pika.BlockingConnection(parameters=parameters)
            channel = connection.channel()
            is_connected = True
        except:
            time.sleep(2)
            is_connected = False
    async def callback(ch, method, properties, body):
        user_data = json.loads(body)
        logger.info(f"{user_data} received")
        user_id = user_data["user_id"]
        complexity = user_data["complexity"]
        queue_name = f'{complexity}_queue'
        
        async with lock:
            curr_queue = complexity_queues[queue_name]
            curr_queue.append(user_data)

            # Check if there are 2 users in the queue
            is_matched = False
            while not is_matched:
                if len(curr_queue) >= 2:
                    user1, user2 = curr_queue[:2]
                    # reply = f'{user1} matched with {user2}'
                    reply = {
                        "user1": f"{user1}",
                        "user2": f"{user2}"
                    }
                    user1_id = user1["user_id"]
                    user2_id = user2["user_id"]
                    curr_queue[:2] = []  # Clear the queue

                    correlation_id = str(properties.correlation_id)
                    # Publish the reply
                    await channel.basic_publish(
                        exchange='',
                        routing_key=f'{user1_id}_q',
                        properties=pika.BasicProperties(
                            correlation_id=properties.correlation_id
                        ),
                        body=json.dumps(reply)
                    )
                    await channel.basic_publish(
                        exchange='',
                        routing_key=f'{user2_id}_q',
                        properties=pika.BasicProperties(
                            correlation_id=properties.correlation_id
                        ),
                        body=json.dumps(reply)
                    )
                    is_matched = True
                else:
                    await asyncio.sleep(1)

    queue_names = ['easy_queue', 'medium_queue', 'hard_queue']

    for name in queue_names:
        channel.queue_declare(queue=name)
        
        channel.basic_consume(
            queue=name,
            on_message_callback=callback,
            auto_ack=True  # Acknowledge message when processed
        )
        
        logger.info(f"{name} ready to accept")
    channel.start_consuming()

    connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)