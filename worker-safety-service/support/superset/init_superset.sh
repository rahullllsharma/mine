#!/bin/bash

# gunicorn default vars
GUNICORN_BIND="0.0.0.0:${SUPERSET_PORT:-8090}"
GUNICORN_LIMIT_REQUEST_FIELD_SIZE=0
GUNICORN_LIMIT_REQUEST_LINE=0
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=300
GUNICORN_WORKERS=${GUNICORN_WORKERS:-5}
# use default worker class "sync" to avoid needing to build image
# GUNICORN_WORKER_CLASS="gevent"

superset db upgrade
superset init

# create service account to access superset rest api
flask fab list-users | grep "username:$SUPERSET_SA" &> /dev/null
if [[ $? != 0 ]]; then
    flask fab create-admin \
        --username="$SUPERSET_SA" \
        --password="$SUPERSET_SA_SECRET" \
        --firstname="service" \
        --lastname="account" \
        --email="system@urbint.com"
fi

gunicorn \
    --timeout "$GUNICORN_TIMEOUT" \
    --limit-request-field_size $GUNICORN_LIMIT_REQUEST_FIELD_SIZE \
    --limit-request-line $GUNICORN_LIMIT_REQUEST_LINE \
    --bind "$GUNICORN_BIND" \
    --threads "$GUNICORN_THREADS" \
    --workers "$GUNICORN_WORKERS" \
    "superset.app:create_app()"
