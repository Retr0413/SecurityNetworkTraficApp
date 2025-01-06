import numpy as np

def preprocess_features(feature_dict):
    """
    feature_dict: {
        "protocol": int,
        "packet_length": int,
        "ttl": int,
        ...
    }
    """
    # 例: 学習時と同じ3特徴量を用いる
    protocol = feature_dict.get("protocol", 0)
    packet_length = feature_dict.get("packet_length", 0)
    ttl = feature_dict.get("ttl", 0)
    return np.array([protocol, packet_length, ttl], dtype=float)
