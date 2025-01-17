import socket
import json
from kafka import KafkaProducer



# Initializing Kafka producer
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Socket connection configuration
HOST = 'localhost'  
PORT = 12345        

try:
    # Connect to the socket server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        while True:
            # Receive data from the server
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            # Parse and send data to Kafka
            try:
                data_list = json.loads(data)
                producer.send('myTopic', data_list)
                producer.flush()  # Ensure the message is sent promptly
                print(f"Message sent to topic {'myTopic'}: {data_list}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

except Exception as e:
    print(f"Error: {e}")
