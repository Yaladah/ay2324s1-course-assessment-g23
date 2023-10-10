import pika
import json
from fastapi import WebSocket
import websockets

from matching_util import User

async def send_user_to_queue(user: User):
    try:
        credentials = pika.PlainCredentials(username='guest', password='guest')
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()

        user_id = user.user_id
        print(user_id)
        complexity = user.complexity
        websocket = user.websocket

        channel.queue_declare(queue=f'{complexity}_queue')
        channel.queue_declare(queue=f'{user_id}_q')

        message = {
            "service": "matching-service",
            "message": f'{user}'
        }
        data = json.dumps(message)

        channel.basic_publish(exchange='', routing_key=f'{complexity}_queue', body=data)
        print(f"{message} sent")
        
        def on_response(ch, method, properties, body):
            if properties.correlation_id == message['correlation_id']:
                response_data = json.load(body)
                websocket.send_text(response_data)
            connection.close()
        
        channel.basic_consume(queue=f'{user_id}_q', on_message_callback=on_response, auto_ack=True)

        connection.close()
        
        return ''
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def listen_for_server_replies(user_id: str):
    credentials = pika.PlainCredentials(username='guest', password='guest')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    # Declare a unique reply queue for this listener
    channel.queue_declare(queue=f'{user_id}_q')

    def on_response(ch, method, properties, body):
        response_data = json.loads(body)
        user1 = response_data['user1']
        user2 = response_data['user2']
        user1.websocket.send_text(f"{user2.user_id}")
        user2.websocket.send_text(f"{user1.user_id}")
        print(f"Received response: {response_data}")
        

    # Consume responses from the unique reply queue
    channel.basic_consume(queue=f'{user_id}_q', on_message_callback=on_response, auto_ack=True)

    print("Listening for server replies...")
    channel.start_consuming()

    connection.close()