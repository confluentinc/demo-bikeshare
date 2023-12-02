from json import dumps

from confluent_kafka import Producer
from rich.progress import track

from journey.data.kafka.utils import filter_timeout_property


def produce(config:dict, topic:str, data:dict, batch_size=50):
    assert isinstance(data,dict)
    
    config = filter_timeout_property(config)    
    producer = Producer(config)
    
    try:
        counter = 0
        for key, object in track(data.items(), description=f'Sending {len(data)} messages to {topic}'):
            producer.produce(topic, key=key, value=dumps(object))
            counter += 1
            
            if counter % batch_size == 0:
                producer.poll()
    except:
        raise
    finally:
        producer.flush()