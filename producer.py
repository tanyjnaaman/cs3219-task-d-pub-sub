from confluent_kafka import Producer
from faker import Faker
import json
import time

fake = Faker()

PORT = 9876

def handle_produce_response(error, message): 
    if error: 
        print(f"Message delivery failed: error")
    
    else: 
        print(f"Message delivered to topic: {message.topic()}")


if __name__ == "__main__":
    # 1. initialize producer
    producer = Producer({
        'bootstrap.servers': f'localhost:{PORT}',
    })
    print("Kafka Producer started.")

    # 2. simulate data being produced
    NUM_DATA = 10
    for i in range(NUM_DATA):
        data={
            'name': fake.name(),
            'address': fake.address(),
            'email': fake.email(),
            'created_at': time.time()
        }
        message = json.dumps(data)

        # check for previous events and calls callback if needed
        # see https://stackoverflow.com/questions/52589772/kafka-producer-difference-between-flush-and-poll
        producer.poll(1) # timout = 1 second

        # send data 
        producer.produce('dummy-user-tracker', message.encode('utf-8'),callback=handle_produce_response)
        producer.flush()
        time.sleep(1) # just sleep for 1s to simulate data being produced


    