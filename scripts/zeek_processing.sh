#!/usr/bin/env bash
PCAP_DIR="/data/pcap"
ZEEK_LOG_DIR="/data/zeek_logs"
mkdir -p $ZEEK_LOG_DIR

latest_pcap=$(ls -t $PCAP_DIR/*.pcap | head -n1)
if [ -f "$latest_pcap" ]; then
    zeek -r "$latest_pcap" local "Log::default_writer=Log::Writer::JSON"
    mv *.log $ZEEK_LOG_DIR
fi
