#!/usr/bin/env bash

# https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425
set -euxo pipefail

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté lista..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 0.1
done
echo "Base de datos lista!"

# Correr migraciones
python -m alembic upgrade head

# Iniciar servidor con múltiples workers
exec uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 4 