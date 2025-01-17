from kafka import KafkaConsumer
import json
import time
from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["SCMproject"]
collection = db["device_data_stream"]


retry_attempts = 5
consumer = None
while retry_attempts > 0:
    try:
        consumer = KafkaConsumer('myTopic', bootstrap_servers='kafka:9092')
        print("Connected to Kafka")
        break
    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        retry_attempts -= 1
        time.sleep(5) 


while True:
    for message in consumer:
        consumed_message = json.loads(message.value.decode("utf-8"))
        print("Recieving.....")
        print(consumed_message)
        device_id = consumed_message.get("device_id")
        source = consumed_message.get("from")
        dest = consumed_message.get("to")
        temp = consumed_message.get("temperature")
        batlevel = consumed_message.get("batterylevel")
        timestamp = consumed_message.get("timestamp")

        obj = {
            "from" : source,
            "to" : dest,
            "temperature" : temp,
            "batteryLevel" : batlevel,
            "timestamp" : timestamp
        }
        
        if collection.find_one({"deviceId" : device_id}):
            collection.find_one_and_update({"deviceId" : device_id},{"$push" : {"readings" : obj}})
        else :
            print(f"Device with device Id"+ device_id +  "not found.")
