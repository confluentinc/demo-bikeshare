from json import dumps
from asyncio import get_event_loop, gather
from datetime import datetime

from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField

from rich import print
from rich.progress import track

from bikeshare.data.kafka.utils import filter_timeout_property

def _generic_error_printing_callback(err, msg):
    if err is not None:
        print(f'Message delivery failed: {msg.key()} - error: {err}')
        
async def _flush_and_kill_producer(producer:Producer):
    producer.flush()
    del producer ## frees up file handlers 

## fanout_size is finnicky and it's not clear what the best value is.  6 seems to work well on my machine for the citibike station status data    
async def multiple_producer_fanout(config:dict, topic:str, data:dict, fanout_size:int=6, set_last_updated_to_now:bool=True,
                                   delivery_callback=_generic_error_printing_callback, data_seralizer=None):
    '''
    Producer is created per message with the same client.id as the key of the message.
    Flushes are fanned out to a pool of `fanout_size` workers.  This seems to work best to be
    close to the number of cores on the machine.
    '''
    assert isinstance(data,dict)
    assert callable(delivery_callback)
    
    config = filter_timeout_property(config)
    data_seralizer = data_seralizer or dumps # default to basic json for topics without schemas
    event_loop = get_event_loop()
    
    counter = 0 
    tasks = []
    for name, object in track(data.items(), description=f'Sending {len(data)} messages to {topic}'):
        
        ## go through each entry, create a new producer with the id of the key and for every `fanout_size` messages, wait for the flush actions to complete
        ## if you do more than this, you quickly get a lot of errors - the flush command is file io intensive and the kafka client doesn't seem to handle
        ## that well when things are running in parallel
        
        config['client.id'] = name
        producer = Producer(config)
        
        if set_last_updated_to_now:
            ## a little fakery to make the consumer look a little more active
            ## in large data batches (NYC) it can take ~10 mins to process all the data
            ## and in the consumer table we're sorting by this, so it wouldn't look right for each
            ## batch to be 10 mins old by the end - plus it ruins the whole "real-time" feel
            object['last_updated'] = int(datetime.now().timestamp())
        
        producer.produce(topic, key=name, value=data_seralizer(object, SerializationContext(topic, MessageField.VALUE)), callback=delivery_callback)
        tasks.append(event_loop.create_task(_flush_and_kill_producer(producer)))
        counter += 1
    
        if counter % fanout_size == 0:
            await gather(*tasks)
            tasks = []