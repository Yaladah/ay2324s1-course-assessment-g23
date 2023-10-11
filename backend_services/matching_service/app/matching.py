import pika
import json
from fastapi import WebSocket
import websockets

from matching_util import User

async def send_user_to_queue(user_id, complexity):
    try:
        credentials = pika.PlainCredentials(username='guest', password='guest')
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()

        channel.queue_declare(queue=f'{complexity}_queue')
        channel.queue_declare(queue=f'{user_id}_q')
        message = {
            "user_id": f"{user_id}",
            "complexity": f"{complexity}"
        }
        data = json.dumps(message)

        channel.basic_publish(exchange='', routing_key=f'{complexity}_queue', body=data)
        connection.close()
        
        return ''
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
def listen_for_server_replies(user_id: str, websocket: WebSocket):
    credentials = pika.PlainCredentials(username='guest', password='guest')
    parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    # Declare a unique reply queue for this listener
    channel.queue_declare(queue=f'{user_id}_q')

    def on_response(ch, method, properties, body):
        response_data = json.loads(body)
        user1 = response_data["user1"]
        user2 = response_data["user2"]
        if user1 == user_id:
            id = user2["user_id"]
            websocket.send_text(json.dumps(id))
        else:
            id = user1["user_id"]
            websocket.send_text(json.dumps(id))
        

    # Consume responses from the unique reply queue
    channel.basic_consume(queue=f'{user_id}_q', on_message_callback=on_response, auto_ack=True)

    print("Listening for server replies...")
    channel.start_consuming()

    connection.close()