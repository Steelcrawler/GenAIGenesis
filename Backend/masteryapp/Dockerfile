FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libmariadb-dev \
    libmariadb-dev-compat \
    build-essential \
    pkg-config \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

    RUN mkdir -p /app/media && chmod 777 /app/media

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/myapp/gcp/genaigenesis-454500-2b74084564ba.json