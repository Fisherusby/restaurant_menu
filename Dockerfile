FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

WORKDIR /app/

# Install packages
RUN apt update && apt install -y wget curl && rm -rf /var/lib/apt/lists/*  \
    && pip install --upgrade pip && pip install --upgrade awscli

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./init_db.sh /init_db.sh
RUN chmod +x /init_db.sh

COPY . /app
