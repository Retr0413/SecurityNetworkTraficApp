import requests
from app.utils.feature_extraction import extract_features_from_zeek_logs

ZEEK_LOG_DIR = "/data/zeek_logs"
API_ENDPOINT = "http://web:5000/api/predict"

if __name__ == "__main__":
    flows = extract_features_from_zeek_logs(ZEEK_LOG_DIR)
    for flow in flows:
        response = requests.post(API_ENDPOINT, json=flow)
        print("Response:", response.json())
