#!/bin/bash
set -o errexit

echo "🔄 Applying database migrations..."
pipenv run python manage.py migrate

echo "🎨 Collecting static files..."
pipenv run python manage.py collectstatic --no-input

# echo "👑 Creating superuser (if not exists)..."
# pipenv run python manage.py createsu

echo "🚀 Starting Gunicorn..."
exec pipenv run gunicorn --config gunicorn-cfg.py core.wsgi
