FROM python:3.13-slim

WORKDIR /app

COPY requirements-docker.txt .

RUN pip install --no-cache-dir --timeout 60 --retries 3 -r requirements-docker.txt

COPY . .

EXPOSE 8000 8501