from flask import Blueprint, jsonify, request
from app.model.model import NetworkTrafficModel
from app.utils.preprocessing import preprocess_features
from app.utils.db import db, TrafficLog
from datetime import datetime
import json
from app.config import Config

api_bp = Blueprint('api', __name__)
model = NetworkTrafficModel(Config.MODEL_PATH)

@api_bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = preprocess_features(data)
    prediction = model.predict(features)

    # ログの保存
    log_entry = TrafficLog(label=prediction, timestamp=datetime.utcnow(), detail=json.dumps(data))
    db.session.add(log_entry)
    db.session.commit()

    return jsonify({'prediction': prediction})