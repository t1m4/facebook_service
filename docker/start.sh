#!/bin/bash
set -e

SERVICE_NAME=Redis SERVICE_HOST=${REDIS_HOST} SERVICE_PORT=${REDIS_PORT} ./docker/wait-for-service.sh
SERVICE_NAME=Postgres SERVICE_HOST=${POSTGRES_HOST} SERVICE_PORT=${POSTGRES_PORT} ./docker/wait-for-service.sh

if [[ $ENVIRONMENT == "local" ]]; then
    exec python manage.py runserver 0.0.0.0:8000 --traceback --insecure
else
    exec gunicorn -b 0.0.0.0:8000 wsgi --timeout=360 --worker-class=gevent --workers ${GUNICORN_WORKERS}
fi
