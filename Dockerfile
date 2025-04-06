FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

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

COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
