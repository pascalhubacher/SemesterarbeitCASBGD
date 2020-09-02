#!/bin/bash
set -e

until nc -vz ${KAFKA_BOOSTRAP_SERVER_NAME} ${KAFKA_BOOSTRAP_SERVER_PORT}; do
  >&2 echo "Waiting for Kafka (${KAFKA_BOOSTRAP_SERVER_NAME} ${KAFKA_BOOSTRAP_SERVER_PORT}) to be ready... - sleeping"
  sleep 2
done

>&2 echo "Kafka is up - executing command"

until nc -vz ${SCHEMA_REGISTRY_SERVER} ${SCHEMA_REGISTRY_SERVER_PORT}; do
  >&2 echo "Waiting for Schema Registry (${SCHEMA_REGISTRY_SERVER} ${SCHEMA_REGISTRY_SERVER_PORT}) to be ready... - sleeping"
  sleep 2
done

>&2 echo "Schema Registry is up"

#exectue create topic
echo "Creating topic if not existent"
python3 create_topic.py

#faust worker script
echo "Starting faust worker_1"
faust -A worker_1 worker -l info