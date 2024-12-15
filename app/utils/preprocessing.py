import numpy as np

def preprocess_features(feature_dict):
    # 例: モデルは "protocol", "packet_length", "ttl" の3特徴量を使うと仮定
    protocol = feature_dict.get("protocol", 0)
    packet_length = feature_dict.get("packet_length", 0)
    ttl = feature_dict.get("ttl", 0)
    return np.array([protocol, packet_length, ttl], dtype=float)
