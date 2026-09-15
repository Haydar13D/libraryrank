#!/bin/sh
set -e

# Auto-generate SSL certs if missing
if [ ! -f /app/cert.pem ] || [ ! -f /app/key.pem ]; then
    echo "[Entrypoint] SSL certificates missing. Generating self-signed SSL cert for libraryrank.ums.ac.id..."
    openssl req -x509 -newkey rsa:2048 -keyout /app/key.pem -out /app/cert.pem -days 365 -nodes -subj "/CN=libraryrank.ums.ac.id"
fi

# Execute CMD passed to container or default gunicorn
if [ $# -gt 0 ]; then
    exec "$@"
else
    exec gunicorn --bind 0.0.0.0:8000 --certfile /app/cert.pem --keyfile /app/key.pem --workers 2 --reload libraryrank.wsgi:application
fi
