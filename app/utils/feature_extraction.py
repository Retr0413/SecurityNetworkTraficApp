import glob
import json

def extract_features_from_zeek_logs(log_dir):
    feature_list = []
    for f in glob.glob(log_dir+"/*.log"):
        with open(f) as fh:
            for line in fh:
                entry = json.loads(line)
                feat = {
                    "Flow Duration": entry.get("duration",0),
                    "Total Fwd Packet": entry.get("orig_pkts",0),
                    "Bwd Packet Length Mean": entry.get("resp_pkts",0) 
                }
                feature_list.append(feat)
    return feature_list