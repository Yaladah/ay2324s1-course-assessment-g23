import pika
import json
from fastapi import WebSocket
import websockets

from matching_util import User

def send_user_to_queue(user: User):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    user_id = user.user_id
    complexity = user.complexity

    channel.queue_declare(queue=f'{complexity}_queue')
    channel.queue_declare(queue=f'{user_id}_q')

    message = {
        "service": "matching-service",
        "message": f'{user}'
    }
    data = json.dumps(message)

    channel.basic_publish(exchange='', routing_key=f'{complexity}_queue', body=data)
    print(f"{message} sent")
    
    # def on_response(ch, method, properties, body):
    #     if properties.correlation_id == message['correlation_id']:
    #         response_data = json.load(body)
    #         # print(data)
    #         websocket.send_text(response_data)
    #     connection.close()
    
    # channel.basic_consume(queue=f'{user_id}_q', on_message_callback=on_response, auto_ack=True)

    connection.close()
    
def listen_for_server_replies():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare a unique reply queue for this listener
    channel.queue_declare(queue='reply_queue')

    def on_response(ch, method, properties, body):
        response_data = json.loads(body)
        user1 = response_data['user1']
        user2 = response_data['user2']
        user1.websocket.send_text(f"You have matched with {user2.user_id}")
        user2.websocket.send_text(f"You have matched with {user1.user_id}")
        # print(f"Received response: {response_data}")
        

    # Consume responses from the unique reply queue
    channel.basic_consume(queue='reply_queue', on_message_callback=on_response, auto_ack=True)

    print("Listening for server replies...")
    channel.start_consuming()
