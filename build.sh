#!/bin/bash
set -o errexit  # Exit on any error

# Install pipenv if not already present
python -m pip install --upgrade pip
pip install pipenv

# Install dependencies from Pipfile
pipenv install

# Collect static files (assuming this is a Django project)
pipenv run python manage.py collectstatic --no-input

# Make migrations and migrate the database
# pipenv run python manage.py makemigrations
pipenv run python manage.py migrate