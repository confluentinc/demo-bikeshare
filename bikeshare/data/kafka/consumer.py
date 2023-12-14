from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField

from rich import print

def consume(cc_config, topic, deseralizer):
    
    cc_config['group.id'] = 'live-updates-consumer'
    # Create a Kafka consumer
    consumer = Consumer(cc_config)

    # Subscribe to a topic
    consumer.subscribe([topic])

    # Start consuming messages
    try:
        while True:
            msg = consumer.poll(5.0)  # Wait for 1 second for new messages
            if msg is not None:
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                ## deserialize the message and yield it
                msg_deseralized = deseralizer(msg.value(),  SerializationContext(msg.topic(), MessageField.VALUE))
                yield msg_deseralized
            else:
                print('No messages received')
            
    finally:
        consumer.close()
