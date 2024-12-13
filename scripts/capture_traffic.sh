#!/usr/bin/env bash
INTERFACE="eth0"
OUTPUT_DIR="/data/pcap"
mkdir -p $OUTPUT_DIR

# tcpdumpを使用してキャプチャ (例)
tcpdump -i $INTERFACE -w $OUTPUT_DIR/cap_$(date +%s).pcap -n
