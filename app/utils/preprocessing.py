import numpy as np

def preprocess_fatures(feature_dict):
    feature_order = ["Flow Duration", "Total Fwd Packet", "Bwd Packet Length Mean"]
    arr = [feature_dict.get(f, 0) for f in feature_order]
    return np.array(arr, dtype=float)