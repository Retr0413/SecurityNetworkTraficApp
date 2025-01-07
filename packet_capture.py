import threading
import time
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP, get_if_list
from db_operations import init_db, save_packets_to_db, get_unprocessed_packets, update_packet_label
from app.model.model import NetworkTrafficModel
from app.utils.preprocessing import preprocess_features
import numpy as np

packet_queue = []
queue_lock = threading.Lock()

def packet_handler(packet):
    if IP in packet:
        ip_layer = packet[IP]
        proto = ip_layer.proto
        ttl = ip_layer.ttl
        flags = None
        src_port = None
        dst_port = None

        if TCP in packet:
            flags = packet.sprintf('%TCP.flags%')
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport

        packet_info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": ip_layer.src,
            "dst_ip": ip_layer.dst,
            "protocol": proto,
            "packet_length": len(packet),
            "ttl": ttl,
            "flags": flags,
            "src_port": src_port,
            "dst_port": dst_port
        }

        with queue_lock:
            packet_queue.append(packet_info)
        print(f"キャプチャ: {packet_info}")

def save_to_db():
    while True:
        to_save = []
        with queue_lock:
            if packet_queue:
                to_save = packet_queue[:]
                packet_queue.clear()
        if to_save:
            save_packets_to_db(to_save)
        time.sleep(5)

def classify_packets():
    model = NetworkTrafficModel("app/model/network_traffic_model.pth")
    while True:
        rows = get_unprocessed_packets()
        if rows:
            ids = []
            feats_list = []
            for r in rows:
                pid, proto, pkt_len, ttl, flags, s_port, d_port = r
                fdict = {
                    "protocol": proto,
                    "packet_length": pkt_len,
                    "ttl": ttl
                }
                feat = preprocess_features(fdict)
                feats_list.append(feat)
                ids.append(pid)

            labels = []
            abnormals = []
            for feat in feats_list:
                label = model.predict(feat)
                # Tor or VPN => 異常とみなす
                abnormal = label in ["Tor","VPN"]
                labels.append(label)
                abnormals.append(abnormal)

            update_packet_label(ids, labels, abnormals)
            print(f"{len(ids)}件のパケットを分類→DB更新")
        time.sleep(5)

def start_sniffing(iface):
    print(f"インターフェース {iface} でスニッフィング開始")
    sniff(iface=iface, prn=packet_handler, store=False)

if __name__ == "__main__":
    init_db()

    db_thread = threading.Thread(target=save_to_db, daemon=True)
    db_thread.start()

    classify_thread = threading.Thread(target=classify_packets, daemon=True)
    classify_thread.start()

    interfaces = get_if_list()
    print(f"利用可能なインターフェース: {interfaces}")
    iface = "eth0" if "eth0" in interfaces else interfaces[0]
    try:
        start_sniffing(iface)
    except KeyboardInterrupt:
        print("パケットキャプチャ停止")
