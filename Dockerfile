# Use official Python base image
FROM python:3.13

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv first
COPY Pipfile* ./
RUN pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --deploy --ignore-pipfile

# Copy project files
COPY . .

# Collect static files
RUN pipenv run python manage.py collectstatic --no-input

# Apply database migrations
RUN pipenv run python manage.py migrate

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["pipenv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
