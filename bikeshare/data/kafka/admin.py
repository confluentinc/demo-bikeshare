from json import dumps, loads

from rich import print

from confluent_kafka import KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.schema_registry.avro import AvroDeserializer

from bikeshare.data.kafka.utils import filter_timeout_property

def create_topic(cc_config, topic, num_partitions=1, replication_factor=3):
    cc_config = filter_timeout_property(cc_config)
    cli = AdminClient(cc_config)
    futures = cli.create_topics([NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor)])
    for topic, future in futures.items():
        try:
            future.result(timeout=10)  # The result itself is None
            print(f'Topic {topic} created')
        except Exception as e:
            # Continue if error code TOPIC_ALREADY_EXISTS, which may be true
            # Otherwise fail fast
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                print(f"Failed to create topic {topic}: {e}")
                exit(1)
            else:
                print(f'Topic {topic} already exists')

def serializer_for_json_schema(sr_config, schema_file, topic):
    sr_client = SchemaRegistryClient(sr_config)
    
    with open(schema_file) as fh:
        schema = loads(fh.read())
    
    schema['title'] = topic
    
    return JSONSerializer(dumps(schema), sr_client)

def deserializer_for_flink_avro_schema(sr_config, schema_file):
    sr_client = SchemaRegistryClient(sr_config)
    
    with open(schema_file) as fh:
        schema = fh.read()

    return AvroDeserializer(sr_client, schema)
    