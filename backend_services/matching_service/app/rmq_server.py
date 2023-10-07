import pika, sys, os, json, time, threading

# create queues for each complexity
complexity_queues = {
    'easy_queue': [],
    'medium_queue': [],
    'hard_queue': [],
}

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        user_data = json.loads(body)
        print(user_data, ' received')
        user = user_data['message']
        complexity = user.complexity
        user_id = user.user_id
        queue_name = f'{complexity}_queue'
        
        with threading.Lock():
            curr_queue = complexity_queues[queue_name]
            curr_queue.append(user)

            # Check if there are 2 users in the queue
            if len(curr_queue) >= 2:
                user1, user2 = curr_queue[:2]
                # reply = f'{user1} matched with {user2}'
                reply = {
                    'user1': f'{user1}',
                    'user2': f'{user2}'
                }
                curr_queue[:2] = []  # Clear the queue

                correlation_id = str(properties.correlation_id)
                # Publish the reply
                channel.basic_publish(
                    exchange='',
                    routing_key='reply_queue',
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