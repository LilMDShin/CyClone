#!/bin/sh
while ! nc -z db 5432; do
    echo "Waiting for the database..."
    sleep 1
done
exec "$@"