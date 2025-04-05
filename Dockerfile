# Use official Python base image
FROM python:3.13

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies & Python dependencies
COPY Pipfile Pipfile.lock ./

RUN apt-get update \
    && apt-get install -y gcc build-essential libpq-dev curl \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pipenv install --deploy --ignore-pipfile \
    && apt-get remove -y gcc build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Apply database migrations
RUN pipenv run python manage.py migrate

# Collect static files
RUN pipenv run python manage.py collectstatic --no-input

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["pipenv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
