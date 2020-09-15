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
echo "Initializing environment (topics)"
python3 initialize_env.py

#
#echo "Create Metadata"
#ksql 'http://localhost:8088' << EOF RUN SCRIPT 'initKafkaTopics.sql'; exit EOF

sleep 90

#simulator
#python3 simulator.py

bash