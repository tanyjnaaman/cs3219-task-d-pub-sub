from confluent_kafka import Consumer

PORT = 9999

if __name__ == "__main__":

    # 1. intialize consumer
    consumer=Consumer({'bootstrap.servers':f'localhost:{PORT}','group.id':'python-consumer','auto.offset.reset':'earliest'})
    print('Kafka Consumer has been initiated.')

    # 2. subscribe to topic
    print('Available topics to consume: ', consumer.list_topics().topics)
    consumer.subscribe(['user-tracker'])

    # 3. consume data
    while True:
        try: 
            message=consumer.poll(1.0) #timeout
            if not message:
                continue
            if message.error():
                print(f"Error: {message.error()}")
                continue
            # all is ok, read
            data=message.value().decode('utf-8')
            print("Received data: ", data)
        finally:
            consumer.close()
            print("Kafka Consumer has been closed.")
