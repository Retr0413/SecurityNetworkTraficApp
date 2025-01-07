FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY db_operations.py db_operations.py
COPY packet_capture.py packet_capture.py
COPY offline_pcap_analysis.py offline_pcap_analysis.py
COPY scripts/ scripts/

ENV FLASK_APP=app/main.py

EXPOSE 5000
