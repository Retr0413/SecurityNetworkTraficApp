FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY scripts/ scripts/

ENV FLASK_APP=app/main.py
EXPOSE 5000
