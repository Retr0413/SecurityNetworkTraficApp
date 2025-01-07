import numpy as np

def preprocess_features(feature_dict):
    """
    feature_dict: {"protocol": int, "packet_length": int, "ttl": int, ...}
    DeepCNNに渡すConv1d入力(1D) => shape=(input_length,) だが、
    ここではprotocol/packet_length/ttlの3要素を例示

    Return: np.array of shape (3,)
    """
    protocol = feature_dict.get("protocol", 0)
    packet_length = feature_dict.get("packet_length", 0)
    ttl = feature_dict.get("ttl", 64)  # 仮に64をデフォルト
    return np.array([protocol, packet_length, ttl], dtype=float)
