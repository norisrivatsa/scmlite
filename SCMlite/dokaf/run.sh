#!/bin/bash

echo "Starting consumer.py..."
python consumer.py &
sleep 2
# Start server.py
echo "Starting server.py..."
python server.py &


# Wait for server.py to initialize
sleep 5  

# Start producer.py
echo "Starting producer.py..."
python producer.py &

wait 

