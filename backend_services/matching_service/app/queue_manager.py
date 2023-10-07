import websockets
from matching_util import User
import pika
import json
import time
from fastapi import WebSocket

# create queues for each complexity
complexity_queues = {
    'easy_queue': {},
    'medium_queue': {},
    'hard_queue': {},
}

def check_for_matches():
    while True:
        for queue_name, user_list in complexity_queues.items():
            if len(user_list) >= 2:
                user1, user2 = user_list[:2]  # Get the first two users
                user_list[:2] = []  # Remove the matched users from the queue
                
                # Notify the matched users with their IDs
                notify_users_of_match(user1, user2)
                print(f"Match Found: {user1['user_id']} and {user2['user_id']}")

        # Sleep for some time before checking again (to avoid busy-waiting)
        time.sleep(1)

def notify_users_of_match(user1: User, user2: User, websocket: websockets):
    user1.websocket.send_text(f"You have matched with {user2.user_id}")
    user2.websocket.send_text(f"You have matched with {user1.user_id}")

def send_user_to_queue(user_id, complexity, websocket: WebSocket):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    queue_name = f'{complexity}_queue'
    channel.queue_declare(queue=queue_name)

    user_data = {
        'user_id' : {user_id},
        'complexity' : {complexity}
    }

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(user_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make the message persistent
        )
    )

    print(f"Sent user to {complexity} queue: {user_id}")

    connection.close()

def consume_queue(queue_name, websocket: WebSocket):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def callback(ch, method, properties, body):
        user_data = json.loads(body)
        complexity = user_data['complexity']
        curr_queue = complexity_queues.get(complexity)
        
        if curr_queue is not None:
            if queue_name not in curr_queue:
                curr_queue[queue_name] = [user_data]
            else:
                curr_queue[queue_name].append(user_data)
                
                # Check if there are 2 users in the queue
                if len(curr_queue[queue_name]) >= 2:
                    user1, user2 = curr_queue[queue_name]
                    notify_users_of_match(user1, user2, websocket)
                    curr_queue[queue_name] = []  # Clear the queue
        
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True  # Acknowledge message when processed
    )

    print(f"Waiting for users in {queue_name}. To exit, press CTRL+C")
    channel.start_consuming()