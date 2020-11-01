from uuid import uuid4
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


####################################################################################
#produce

def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.
    Args:
        err (KafkaError): The error that occurred on None on success.
        msg (Message): The message that was produced or failed.
    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))

schema_str = """
    {
        "name": "rawGames",
        "type": "record",
        "fields": [
            {"name": "ts", "type": "string"},
            {"name": "x", "type": "float"},
            {"name": "y", "type": "float"},
            {"name": "z", "type": "float"},
            {"name": "id", "type": "int"},
            {"name": "matchid", "type": "int"}
        ]
    }
    """

SCHEMA_REGISTRY_URL = "http://schema-registry-1:8081"
BROKER = "kafka-1:9092"
topic = "rawGames"

schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_serializer = AvroSerializer(schema_str, schema_registry_client)

producer_conf = {'bootstrap.servers': BROKER,
                    'key.serializer': StringSerializer('utf_8'),
                    'value.serializer': avro_serializer}

producer = SerializingProducer(producer_conf)

print("Producing user records to topic {}. ^C to exit.".format(topic))
# Serve on_delivery callbacks from previous calls to produce()
producer.poll(0.0)
#{"ts": "2018-06-29T08:15:27.243860", "x": "-0.38", "y": "-2.23", "z": "0.0", "id": "200", "matchid": "19060518"}
producer.produce(topic=topic, key=str(uuid4()), value={"ts": "2018-06-29T08:15:27.243860", "x": -0.38, "y": -2.23, "z": 0.0, "id": 200, "matchid": 19060518}, on_delivery=delivery_report)
    
print("\nFlushing records...")
producer.flush()

####################################################################################
#consume
"""Consumes data from the Kafka Topic"""
#
#     Create a CachedSchemaRegistryClient
#
#schema_registry = CachedSchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

#
#     Use the Avro Consumer
#
#c = AvroConsumer({"bootstrap.servers": BROKER_URL, "group.id": "0"},schema_registry=schema_registry,)
#c.subscribe([topic_name])