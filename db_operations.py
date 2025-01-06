import os
import time
import pymysql

DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_NAME = os.environ.get("DB_NAME", "app_db")

def init_db():
    for i in range(10):
        try:
            conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
            conn.close()
            print("DB接続に成功")
            return
        except Exception as e:
            print(f"DB接続失敗: {e}。再試行...")
            time.sleep(5)
    raise Exception("DB接続に失敗しました")

def save_packets_to_db(packet_list):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO traffic_log
    (timestamp, src_ip, dst_ip, protocol, packet_length, ttl, flags, src_port, dst_port)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data_to_insert = []
    for p in packet_list:
        data_to_insert.append(
            (p["timestamp"], p["src_ip"], p["dst_ip"], p["protocol"], p["packet_length"],
             p["ttl"], p["flags"], p["src_port"], p["dst_port"])
        )
    if data_to_insert:
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        print(f"{len(data_to_insert)}件のパケットをDBに保存")
    cursor.close()
    conn.close()

def get_unprocessed_packets():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    select_sql = """
    SELECT id, protocol, packet_length, ttl, flags, src_port, dst_port
    FROM traffic_log
    WHERE processed = FALSE
    """
    cursor.execute(select_sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_packet_label(ids, labels, is_abnormals):
    """
    labels: 各行に対応するクラス名 (Non-Tor/NonVPN/VPN/Tor)
    is_abnormals: True/False
    """
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    for packet_id, label, abnormal in zip(ids, labels, is_abnormals):
        update_sql = """
        UPDATE traffic_log SET label=%s, processed=TRUE, is_abnormal=%s
        WHERE id=%s
        """
        cursor.execute(update_sql, (label, abnormal, packet_id))
    conn.commit()
    cursor.close()
    conn.close()
