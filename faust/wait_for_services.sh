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

#read the t_rawMetaPlayer topic and save the playerinfo locally as player.json
#python3 GetPlayers2Json.py

#faust worker script
#>&2 echo "Starting faust worker listening on RawGames and send it in the background
#faust -A worker_fbRawGames worker -l info --without-web &
#>&2 echo "Starting faust worker listening on fbBallPossession and send it in the background
#faust -A worker_fbBallPossession worker -l info --without-web &
bash