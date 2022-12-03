#!/bin/bash

SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh
SERVICE_NAME=Postgres SERVICE_HOST=${POSTGRES_HOST} SERVICE_PORT=${POSTGRES_PORT} ./docker/wait-for-service.sh

exec celery -A facebook_service flower --address=127.0.0.1 --port=5555
