from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient, NewTopic


def parse_cc_config_file(config_file):
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
                print(f"Failed to create topic {topic}: {e}")
                exit(1)
