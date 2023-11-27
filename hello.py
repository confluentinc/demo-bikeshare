from uuid import uuid4
from sys import argv
from time import sleep
from confluent_kafka import Producer, Consumer

config_path="/etc/opt/demo/client.properties"
# config_path="client.properties"

def read_ccloud_config_data(config_file):
    omitted_fields = set(['schema.registry.url', 'basic.auth.credentials.source', 'basic.auth.user.info'])
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                if parameter not in omitted_fields:
                    conf[parameter] = value.strip()
    return conf


def produce(topic):
    producer = Producer(read_ccloud_config_data(config_path))
    
    try:
        while True:
            value = str(uuid4())
            print(f'Sending: topic->{topic} | key->keyName | value->{value}')
            producer.produce(topic, key="keyName", value=value)
            producer.flush()
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()

def consume(topic):
    props = read_ccloud_config_data(config_path)
    props["group.id"] = "python-group-1"
    props["auto.offset.reset"] = "earliest"
    consumer = Consumer(props)
    consumer.subscribe([topic])
    try:
        while True:
            msg = consumer.poll(2)
            if msg is not None and msg.error() is None:
                key, value = msg.key().decode('utf-8'), msg.value().decode('utf-8')
                print(f"Received: topic->{topic} key->{key} value->{value}")
            else:
                print(f'no message received by consumer for topic: {topic}')
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        
if __name__ == "__main__":

    ## parse out command and optional topic name
    if len(argv) < 2 or argv[1] not in ["produce", "consume"]:
        print("Provide produce/consume as first argument")
        exit(1)
    if len(argv) > 3:
        print("usage: produce/consume <topic> (optional)")
        exit(1)
    if len(argv) == 2:
        topic = 'demo-topic'
    else:
        topic = argv[2]
        
    command = argv[1]
    
    ## run corresponding action
    match command:
        case "produce":
            produce(topic)
        case "consume":
            consume(topic)
