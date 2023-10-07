import pika
import json
import time
import threading

def send_user_to_queue(user_id, complexity):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # channel.queue_declare(queue='hello')

    # channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    # print(" [x] Sent 'Hello World!'")

    channel.queue_declare(queue=f'{complexity}_queue')
    channel.queue_declare(queue=f'{user_id}_q')

    message = {
        "service": "matching-service",
        "message": {
            "user_id": f"{user_id}",
            "complexity": f"{complexity}"
        }
    }

    # message = {
    #     "service": "matching-service",
    #     "message": {
    #         "user_id": "123",
    #         "complexity": "easy"
    #     }
    # }
    data = json.dumps(message)

    channel.basic_publish(exchange='', routing_key=f'{complexity}_queue', body=data)
    print(f"{message} sent")
    
    # response_data = None
    
    def on_response(ch, method, properties, body):
        # nonlocal response_data
        if properties.correlation_id == message['correlation_id']:
            response_data = json.load(body)
            print(data)
        connection.close()
    
    channel.basic_consume(queue=f'{user_id}_q', on_message_callback=on_response, auto_ack=True)

    # while response_data is None:
    #     connection.process_data_events()
    #     time.sleep(0.1)  # You can adjust the sleep interval as needed

    connection.close()
    
def listen_for_server_replies():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare a unique reply queue for this listener
    # reply_queue = channel.queue_declare(exclusive=True).method.queue
    channel.queue_declare(queue='reply_queue')

    def on_response(ch, method, properties, body):
        response_data = json.loads(body)
        print(f"Received response: {response_data}")

    # Consume responses from the unique reply queue
    channel.basic_consume(queue='reply_queue', on_message_callback=on_response, auto_ack=True)

    print("Listening for server replies...")
    channel.start_consuming()
    
listener_thread = threading.Thread(target=listen_for_server_replies)
listener_thread.start()    

send_user_to_queue("test1", "easy")
print('test1 added')
time.sleep(2)
send_user_to_queue("pain1", "easy")
print('pain1 added')

