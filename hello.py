from uuid import uuid4
from sys import argv
from time import sleep
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic


def parse_config_file(config_file):
    ## remove schema registry params from config as it causes an error later
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

def create_topic(conf, topic, num_partitions=1, replication_factor=3):
    cli = AdminClient(conf)

    futures = cli.create_topics([NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)])
    for topic, future in futures.items():
        try:
            future.result()  # The result itself is None
            print(f'Topic {topic} created')
        except Exception as e:
            # Continue if error code TOPIC_ALREADY_EXISTS, which may be true
            # Otherwise fail fast
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                print("Failed to create topic {}: {}".format(topic, e))
                sys.exit(1)


def produce(config, topic):
    producer = Producer(config)
    
    try:
        while True:
            value = str(uuid4())
            print(f'Sending: topic->{topic} | key->keyName | value->{value}')
            producer.produce(topic, key="keyName", value=value)
            producer.poll()
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()

def consume(config, topic):
    config["group.id"] = "python-group-1"
    config["auto.offset.reset"] = "earliest"
    
    consumer = Consumer(config)
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
    
    ## TODO: make this part of the default config in the cli with cleo    
    config_path="/etc/opt/demo/client.properties"
    # config_path="client.properties"
    config = parse_config_file(config_path)

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
    
    ## create topic if it doesn't exist
    create_topic(config, topic)
    
    ## run corresponding action
    match command:
        case "produce":
            produce(config, topic)
        case "consume":
            consume(config, topic)
