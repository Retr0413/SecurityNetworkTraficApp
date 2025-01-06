import sys
import logging
from scapy.all import *
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
import numpy as np

# 追加: DB操作と機械学習モデル
from db_operations import init_db, save_packets_to_db
from app.model.model import NetworkTrafficModel
from app.utils.preprocessing import preprocess_features

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def read_pcap(pcap_file):
    try:
        packets = rdpcap(pcap_file)
    except FileNotFoundError:
        logger.error(f"PCAP file not found: {pcap_file}")
        sys.exit(1)
    except Scapy_Exception as e:
        logger.error(f"Error reading PCAP file: {e}")
        sys.exit(1)
    return packets

def extract_packet_data(packets):
    packet_data = []
    for packet in tqdm(packets, desc="Processing packets", unit="packet"):
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = packet[IP].proto
            size = len(packet)
            packet_data.append({"src_ip": src_ip, "dst_ip": dst_ip, "protocol": protocol, "size": size})
    return pd.DataFrame(packet_data)

def protocol_name(number):
    protocol_dict = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
    return protocol_dict.get(number, f"Unknown({number})")

def analyze_packet_data(df):
    total_bandwidth = df["size"].sum()
    protocol_counts = df["protocol"].value_counts(normalize=True) * 100
    protocol_counts.index = protocol_counts.index.map(protocol_name)

    ip_communication = df.groupby(["src_ip", "dst_ip"]).size().sort_values(ascending=False)
    ip_communication_percentage = ip_communication / ip_communication.sum() * 100
    ip_communication_table = pd.concat([ip_communication, ip_communication_percentage], axis=1).reset_index()
    ip_communication_table.columns = ["src_ip", "dst_ip", "Count", "Percentage"]

    protocol_frequency = df["protocol"].value_counts()
    protocol_frequency.index = protocol_frequency.index.map(protocol_name)

    protocol_counts_df = pd.concat([protocol_frequency, protocol_counts], axis=1).reset_index()
    protocol_counts_df.columns = ["Protocol", "Count", "Percentage"]

    # ip_communication_protocols
    ip_proto_df = df.groupby(["src_ip", "dst_ip", "protocol"]).size().reset_index(name="Count")
    ip_proto_df["Protocol"] = ip_proto_df["protocol"].apply(protocol_name)
    ip_proto_df["Percentage"] = ip_proto_df.groupby(["src_ip", "dst_ip"])["Count"].apply(lambda x: x / x.sum() * 100)
    
    return total_bandwidth, protocol_counts_df, ip_communication_table, protocol_frequency, ip_proto_df

def detect_port_scanning(packets, port_scan_threshold=100):
    # Example: we won't store in DataFrame but do minimal logic
    # If we want a full logic, we can reuse `extract_packet_data_security` approach
    port_dict = {}
    for packet in tqdm(packets, desc="Detecting port scanning", unit="packet"):
        if IP in packet and TCP in packet:
            src_ip = packet[IP].src
            dst_port = packet[TCP].dport
            port_dict.setdefault(src_ip, set()).add(dst_port)
    suspicious_ips = [ip for ip, ports in port_dict.items() if len(ports) >= port_scan_threshold]
    if suspicious_ips:
        logger.warning(f"Potential port scanning: {suspicious_ips}")

def print_results(total_bandwidth, protocol_counts_df, ip_communication_table):
    # bandwidth in Bytes => convert to MB or GB
    if total_bandwidth < 10**9:
        bandwidth_unit = "MB"
        total_bandwidth /= 10**6
    else:
        bandwidth_unit = "GB"
        total_bandwidth /= 10**9

    logger.info(f"\nTotal bandwidth used: {total_bandwidth:.2f} {bandwidth_unit}")

    logger.info("\nProtocol Distribution:\n")
    logger.info(tabulate(protocol_counts_df, headers=["Protocol", "Count", "Percentage"], tablefmt="grid"))

    logger.info("\nTop IP Address Communications:\n")
    logger.info(tabulate(ip_communication_table, headers=["Source IP","Destination IP","Count","Percentage"], tablefmt="grid", floatfmt=".2f"))

def save_to_db_for_model(df):
    """
    df columns: [src_ip, dst_ip, protocol, size]
    We want to store them in 'traffic_log' table via db_operations.save_packets_to_db
    """
    # Convert each row to a dict
    packet_list = []
    for _, row in df.iterrows():
        packet_list.append({
            "timestamp": "OfflinePCAP",  # or some time extraction from packet
            "src_ip": row["src_ip"],
            "dst_ip": row["dst_ip"],
            "protocol": int(row["protocol"]),
            "packet_length": int(row["size"]),
            "ttl": 64,   # offline approximation
            "flags": None,
            "src_port": None,
            "dst_port": None
        })
    # save to DB
    from db_operations import save_packets_to_db
    save_packets_to_db(packet_list)

def classify_offline_packets():
    """
    After we save offline pcap data into DB,
    we do a single pass classification for all unprocessed records
    """
    from db_operations import get_unprocessed_packets, update_packet_label
    from app.model.model import NetworkTrafficModel
    from app.utils.preprocessing import preprocess_features

    model = NetworkTrafficModel("app/model/network_traffic_model.pth")

    rows = get_unprocessed_packets()
    if rows:
        ids = []
        feats_list = []
        for r in rows:
            # r: (id, protocol, packet_length, ttl, flags, src_port, dst_port)
            (pid, proto, pkt_len, ttl, flags, s_port, d_port) = r
            fdict = {
                "protocol": proto,
                "packet_length": pkt_len,
                "ttl": ttl
            }
            feat = preprocess_features(fdict)
            feats_list.append(feat)
            ids.append(pid)

        labels = []
        is_abnormals = []
        for feat in feats_list:
            label = model.predict(feat)
            # "Tor" / "VPN" => abnormal
            abnormal = (label in ["Tor", "VPN"])
            labels.append(label)
            is_abnormals.append(abnormal)

        update_packet_label(ids, labels, is_abnormals)
        logger.info(f"Offline classification done for {len(ids)} packets")
    else:
        logger.info("No unprocessed packets found in DB")

def main(pcap_file, port_scan_threshold=100):
    from db_operations import init_db
    # Initialize DB connection
    init_db()

    # 1. read pcap
    packets = read_pcap(pcap_file)
    # 2. analyze general stats
    df = extract_packet_data(packets)
    total_bandwidth, protocol_counts_df, ip_comm_table, protocol_freq, ip_proto_df = analyze_packet_data(df)
    print_results(total_bandwidth, protocol_counts_df, ip_comm_table)
    # 3. detect port scanning
    detect_port_scanning(packets, port_scan_threshold)
    # 4. optional: store data in DB => model classification
    logger.info("Saving offline pcap data to DB...")
    save_to_db_for_model(df)
    logger.info("Running classification on saved records...")
    classify_offline_packets()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python offline_pcap_analysis.py <pcap_file> [port_scan_threshold]")
        sys.exit(1)

    pcap_file = sys.argv[1]
    threshold = 100
    if len(sys.argv) >= 3:
        threshold = int(sys.argv[2])

    main(pcap_file, threshold)
