from uuid import uuid4
from confluent_kafka import Producer, Consumer

config_path="/etc/opt/demo/client.properties"

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
    print(f'produce(topic={topic})')
    producer = Producer(read_ccloud_config_data(config_path))
    producer.produce(topic, key="key", value=str(uuid4()))
    producer.flush()

def consume(topic):
    print(f'consume(topic={topic}))')
    props = read_ccloud_config_data(config_path)
    props["group.id"] = "python-group-1"
    props["auto.offset.reset"] = "earliest"
    print('before consumer init')
    consumer = Consumer(props)
    consumer.subscribe([topic])
    try:
        print('inside try')
        while True:
            print('inside while True')
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                print("key = {key:12} value = {value:12}".format(key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
            else:
                print('no message received by consumer')
    except KeyboardInterrupt:
        print('keyboard interrupt')
        pass
    finally:
        consumer.close()
        
if __name__ == "__main__":
    print('begin')
    topic = "demo-topic"
    produce(topic)
    consume(topic)