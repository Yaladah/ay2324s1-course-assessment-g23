import pika, sys, os, json, time, threading

# create queues for each complexity
complexity_queues = {
    'easy_queue': [],
    'medium_queue': [],
    'hard_queue': [],
}

def main():
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    # channel = connection.channel()

    # channel.queue_declare(queue='hello')

    # def callback(ch, method, properties, body):
    #     print(f" [x] Received {body}")

    # channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    # print(' [*] Waiting for messages. To exit press CTRL+C')
    # channel.start_consuming()
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        # user_data = json.loads(body)
        # print(user_data, ' received')
        # message = user_data['message']
        # complexity = message['complexity']
        # user_id = message['user_id']
        # queue_name = f'{complexity}_queue'
        # curr_queue = complexity_queues[queue_name]
        
        # if curr_queue is not None:
        #     # if queue_name not in curr_queue:
        #     #     curr_queue[queue_name].append(user_id)
        #     # else:
        #     curr_queue.append(user_id)
                
        #     # Check if there are 2 users in the queue
        #     while len(curr_queue) < 2:
        #         time.sleep(0.5)
        #     user1, user2 = curr_queue
        #     reply = f'{user1} matched with {user2}'
        #     # notify_users_of_match(user1, user2, websocket)
        #     curr_queue = []  # Clear the queue
                

        # channel.basic_publish(
        #     exchange='',
        #     routing_key=properties.reply_to,
        #     properties=pika.BasicProperties(
        #     correlation_id=properties.correlation_id
        #     ),
        #     body=json.dumps(reply)
        # )
        
        # ch.basic_ack(delivery_tag=method.delivery_tag)
        user_data = json.loads(body)
        print(user_data, ' received')
        message = user_data['message']
        complexity = message['complexity']
        user_id = message['user_id']
        queue_name = f'{complexity}_queue'
        
        with threading.Lock():
            curr_queue = complexity_queues[queue_name]
            curr_queue.append(user_id)

            # Check if there are 2 users in the queue
            if len(curr_queue) >= 2:
                user1, user2 = curr_queue[:2]
                reply = f'{user1} matched with {user2}'
                curr_queue[:2] = []  # Clear the queue

                routing_key = str(properties.reply_to)
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