#!/usr/bin/env bash

set -e

until pg_isready --host="${POSTGRES_HOST}" --username="${POSTGRES_USER}" --quiet; do
    sleep 1;
done

echo "Postgres database is up."

touch -a /sagexit/log/uwsgi.log
touch -a /sagexit/log/django.log

cd /sagexit/src/website/

./manage.py compilescss
./manage.py collectstatic --no-input -v0 --ignore="*.scss"
./manage.py migrate --no-input

chown --recursive www-data:www-data /sagexit/

echo "Starting uwsgi server."
uwsgi --chdir=/sagexit/src/website \
    --module=sagexit.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --socket=:8000 \
    --processes=5 \
    --uid=www-data --gid=www-data \
    --harakiri=600 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --logfile-chown \
    --logto2=/sagexit/log/uwsgi.log \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception \
    --enable-threads
