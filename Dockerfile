FROM python:3.10-slim

WORKDIR /app/

# Install packages
RUN apt update && apt install -y wget curl && rm -rf /var/lib/apt/lists/*  \
    && pip install --upgrade pip && pip install --upgrade awscli && pip install uvicorn

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./start_reload.sh /start_reload.sh

RUN chmod +x /start_reload.sh

COPY . /app
