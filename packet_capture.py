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
        ttl = ip_layer.ttl
        proto = ip_layer.proto
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
    # 未処理データをモデルで判定して更新
    model = NetworkTrafficModel("app/model/network_traffic_model.pth")
    while True:
        rows = get_unprocessed_packets() # (id, protocol, packet_length, ttl, flags, src_port, dst_port)
        if rows:
            ids = []
            features_list = []
            for r in rows:
                pid = r[0]
                protocol = r[1]
                packet_length = r[2]
                ttl = r[3]
                # flags = r[4] 未使用例
                # src_port = r[5], dst_port = r[6] 未使用例
                # 必要に応じてfeature_dictに追加
                feature_dict = {
                    "protocol": protocol,
                    "packet_length": packet_length,
                    "ttl": ttl
                }
                feat = preprocess_features(feature_dict)
                features_list.append(feat)
                ids.append(pid)

            labels = []
            for x in features_list:
                label = model.predict(x)
                labels.append(label)

            update_packet_label(ids, labels)
            print(f"{len(ids)}件のパケットを判定しラベル付け: {list(zip(ids, labels))}")

        time.sleep(5)

def start_sniffing(interface):
    print(f"{interface}でスニッフィング開始")
    sniff(iface=interface, prn=packet_handler, store=False)

if __name__ == "__main__":
    init_db()

    db_thread = threading.Thread(target=save_to_db, daemon=True)
    db_thread.start()

    classify_thread = threading.Thread(target=classify_packets, daemon=True)
    classify_thread.start()

    interfaces = get_if_list()
    print("利用可能なインターフェース:", interfaces)
    iface = "eth0" if "eth0" in interfaces else interfaces[0]

    try:
        start_sniffing(iface)
    except KeyboardInterrupt:
        print("停止します")
