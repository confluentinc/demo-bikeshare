from json import dumps, loads

from rich import print

from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from journey.data.kafka.utils import filter_timeout_property

def create_topic_if_needed(cc_config, topic, num_partitions=1, replication_factor=3):
    cc_config = filter_timeout_property(cc_config)
    cli = AdminClient(cc_config)

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

def seralizer_for_schema(sr_config, schema_file, topic):
    sr_client = SchemaRegistryClient(sr_config)
    
    with open(schema_file) as fh:
        schema = loads(fh.read())
    
    schema['title'] = topic
    
    return JSONSerializer(dumps(schema), sr_client)
        
    