from confluent_kafka import avro, Consumer, Producer
from confluent_kafka.avro import AvroConsumer, AvroProducer, CachedSchemaRegistryClient


####################################################################################
#produce

#
# Load the schema using the Confluent avro loader
# See: https://github.com/confluentinc/confluent-kafka-python/blob/master/confluent_kafka/avro/load.py#L23
#
schema = avro.loads(
    """{
    "type": "record",
    "name": "click_event",
    "namespace": "com.udacity.lesson3.solution4",
    "fields": [
        {"name": "email", "type": "string"},
        {"name": "timestamp", "type": "string"},
        {"name": "uri", "type": "string"},
        {"name": "number", "type": "int"},
        {
            "name": "attributes",
            "type": {
                "type": "map",
                "values": {
                    "type": "record",
                    "name": "attribute",
                    "fields": [
                        {"name": "element", "type": "string"},
                        {"name": "content", "type": "string"}
                    ]
                }
            }
        }
    ]
}"""
)

    #
#       Create a CachedSchemaRegistryClient. Use SCHEMA_REGISTRY_URL.
# See: https://github.com/confluentinc/confluent-kafka-python/blob/master/confluent_kafka/avro/cached_schema_registry_client.py#L47
#
schema_registry = CachedSchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

#
#       Replace with an AvroProducer.
# See: https://docs.confluent.io/current/clients/confluent-kafka-python/index.html?highlight=loads#confluent_kafka.avro.AvroProducer
#
p = AvroProducer({"bootstrap.servers": BROKER_URL}, schema_registry=schema_registry)

p.produce(topic=topic_name, value=asdict(ClickEvent()), value_schema=ClickEvent.schema)

####################################################################################
#consume
"""Consumes data from the Kafka Topic"""
#
#     Create a CachedSchemaRegistryClient
#
schema_registry = CachedSchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

#
#     Use the Avro Consumer
#
c = AvroConsumer(
    {"bootstrap.servers": BROKER_URL, "group.id": "0"},
    schema_registry=schema_registry,
)
c.subscribe([topic_name])