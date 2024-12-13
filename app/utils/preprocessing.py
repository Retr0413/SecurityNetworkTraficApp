import numpy as np

def preprocess_features(feature_dict):
    # ここでfeature_dictから必要な特徴量を抽出し、numpy array等に変換する処理を行う
    # 例:
    feature_order = ["Flow Duration", "Total Fwd Packet", "Bwd Packet Length Mean"]
    arr = [feature_dict.get(f, 0) for f in feature_order]
    return np.array(arr, dtype=float)