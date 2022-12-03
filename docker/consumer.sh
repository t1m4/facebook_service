#!/bin/bash

if [[ $ENVIRONMENT == "local" ]]; then
  SERVICE_NAME=Kafka SERVICE_HOST=${KAFKA_HOST} SERVICE_PORT=${KAFKA_PORT} ./docker/wait-for-service.sh
fi
SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh
SERVICE_NAME=Postgres SERVICE_HOST=${POSTGRES_HOST} SERVICE_PORT=${POSTGRES_PORT} ./docker/wait-for-service.sh

DJANGO_SETTINGS_MODULE=facebook_service.settings python kafka_consumer.py
