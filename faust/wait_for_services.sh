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

>&2 echo "Wait 60 seconds to start the faust agent up"
#sleep 60

#cd ./data-transfer

#faust worker script
>&2 echo "Starting faust worker listening on RawGames"
#faust -A worker_fbRawGames worker -l info --without-web &
#faust -A worker_fbRawGames2 worker -l info --without-web &
bash