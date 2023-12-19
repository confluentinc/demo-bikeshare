from collections.abc import Callable, Iterable

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField

from rich import print

def consume(cc_config:dict, topic:str, deseralizer:Callable, consumer_id:str, poll_interval:int) -> Iterable[dict]:
    cc_config['group.id'] = consumer_id
    consumer = Consumer(cc_config)
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(poll_interval)
            if msg is not None:
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                msg_deseralized = deseralizer(msg.value(),  SerializationContext(msg.topic(), MessageField.VALUE))
                yield msg_deseralized
            else:
                yield msg
    finally:
        consumer.close()
