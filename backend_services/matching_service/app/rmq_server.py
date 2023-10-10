import pika, sys, os, json, time, threading
import asyncio

# create queues for each complexity
complexity_queues = {
    'easy_queue': [],
    'medium_queue': [],
    'hard_queue': [],
}

lock = asyncio.Lock()

def main():
    credentials = pika.PlainCredentials(username='guest', password='guest')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    async def callback(ch, method, properties, body):
        user_data = json.loads(body)
        print(user_data, ' received')
        user = user_data['message']
        complexity = user.complexity
        user_id = user.user_id
        queue_name = f'{complexity}_queue'
        
        with lock:
            curr_queue = complexity_queues[queue_name]
            curr_queue.append(user)

            # Check if there are 2 users in the queue
            if len(curr_queue) >= 2:
                user1, user2 = curr_queue[:2]
                # reply = f'{user1} matched with {user2}'
                reply = {
                    "user1": f'{user1}',
                    "user2": f'{user2}'
                }
                user1_id = user1.user_id
                user2_id = user2.user_id
                curr_queue[:2] = []  # Clear the queue

                correlation_id = str(properties.correlation_id)
                # Publish the reply
                channel.basic_publish(
                    exchange='',
                    routing_key=f'{user1_id}_q',
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(reply)
                )
                channel.basic_publish(
                    exchange='',
                    routing_key=f'{user2_id}_q',
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(reply)
                )

        # channel.basic_ack(delivery_tag=method.delivery_tag)

    queue_names = ['easy_queue', 'medium_queue', 'hard_queue']

    for name in queue_names:
        channel.queue_declare(queue=name)
        
        channel.basic_consume(
            queue=name,
            on_message_callback=callback,
            auto_ack=True  # Acknowledge message when processed
        )
        
        print(f'{name} ready to accept')
    
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