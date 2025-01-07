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
    """
    packet_list: [{"timestamp":..., "src_ip":..., "dst_ip":..., "protocol":..., "packet_length":..., ...}, ...]
    """
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    insert_sql = """
    INSERT INTO traffic_log
    (timestamp, src_ip, dst_ip, protocol, packet_length, ttl, flags, src_port, dst_port)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    data = []
    for p in packet_list:
        data.append((
            p.get("timestamp",""),
            p.get("src_ip",""),
            p.get("dst_ip",""),
            p.get("protocol",0),
            p.get("packet_length",0),
            p.get("ttl",0),
            p.get("flags",None),
            p.get("src_port",None),
            p.get("dst_port",None)
        ))
    if data:
        cursor.executemany(insert_sql, data)
        conn.commit()
        print(f"{len(data)}件のパケットをDBに保存")
    cursor.close()
    conn.close()

def get_unprocessed_packets():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    sql = """
    SELECT id, protocol, packet_length, ttl, flags, src_port, dst_port
    FROM traffic_log
    WHERE processed = FALSE
    """
    cursor.execute(sql)
    rows = cursor.fetchall()  # [(id,protocol,packet_length,ttl,flags,src_port,dst_port), ...]
    cursor.close()
    conn.close()
    return rows

def update_packet_label(ids, labels, is_abnormals):
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    for packet_id, label, abnormal in zip(ids, labels, is_abnormals):
        up_sql = """
        UPDATE traffic_log
        SET label=%s, processed=TRUE, is_abnormal=%s
        WHERE id=%s
        """
        cursor.execute(up_sql, (label, abnormal, packet_id))
    conn.commit()
    cursor.close()
    conn.close()
