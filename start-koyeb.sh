#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py seed_demo
python manage.py ensure_admin

exec daphne study_girl.asgi:application --bind 0.0.0.0 --port "${PORT:-8000}"
