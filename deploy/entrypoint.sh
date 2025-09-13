#!/usr/bin/env bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-coachapp.settings}

python --version
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# DB migrate (best-effort; can be disabled via env)
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
fi

# Collect static
if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  echo "Collecting static..."
  python manage.py collectstatic --noinput
fi

WORKERS=${GUNICORN_WORKERS:-3}
THREADS=${GUNICORN_THREADS:-2}
TIMEOUT=${GUNICORN_TIMEOUT:-60}

exec gunicorn coachapp.wsgi:application \
  --workers "$WORKERS" --threads "$THREADS" --timeout "$TIMEOUT" \
  --bind 0.0.0.0:8000

