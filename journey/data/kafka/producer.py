from json import dumps

from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField

from rich import print
from rich.progress import track

from journey.data.kafka.utils import filter_timeout_property

def _generic_error_printing_callback(err, msg):
    if err is not None:
        print(f'Message delivery failed: {msg.key()} - error: {err}')

def produce(config:dict, topic:str, data:dict, batch_size:int=50, delivery_callback=_generic_error_printing_callback, data_seralizer=None):
    assert isinstance(data,dict)
    
    config = filter_timeout_property(config)    
    producer = Producer(config)
    data_seralizer = data_seralizer or dumps # default to basic json for topics without schemas
    
    try:
        counter = 0
        for key, object in track(data.items(), description=f'Sending {len(data)} messages to {topic}'):
            producer.produce(topic, key=key, value=data_seralizer(object, SerializationContext(topic, MessageField.VALUE)), callback=delivery_callback)
            counter += 1
            
            if counter % batch_size == 0:
                producer.poll()
    finally:
        producer.flush()
        