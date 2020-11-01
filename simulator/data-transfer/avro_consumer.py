import requests
import json

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

####################################################################################
#consume

SCHEMA_REGISTRY_URL = "http://schema-registry-1:8081"
BROKER = "kafka-1:9092"
topic = "rawGames"

#get schema from schema registry
URL = SCHEMA_REGISTRY_URL + '/subjects/' + topic + '-value/versions/latest/schema'
r = requests.get(url=URL)
schema_str = json.dumps(r.json())

sr_conf = {"url": SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(sr_conf)

avro_deserializer = AvroDeserializer(schema_str, schema_registry_client)
string_deserializer = StringDeserializer('utf_8')

consumer_conf = {'bootstrap.servers': BROKER,
                    'key.deserializer': string_deserializer,
                    'value.deserializer': avro_deserializer,
                    'group.id': '0',
                    'auto.offset.reset': "earliest"}

consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe([topic])

while True:
    try:
        # SIGINT can't be handled when polling, limit timeout to 1 second.
        msg = consumer.poll(1.0)
        if msg is None:
            continue

        print('key:', msg.key(), 'value:', msg.value())
    except KeyboardInterrupt:
        break

consumer.close()