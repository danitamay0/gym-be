#!/usr/bin/env bash
set -e

# 1) Aplicar migraciones
flask --app app:create_app db upgrade

# 2) Arrancar Gunicorn
exec python -m gunicorn --chdir /app/app --workers 3 --bind 0.0.0.0:8000 app:app