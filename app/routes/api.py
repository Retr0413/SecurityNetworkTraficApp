# app/routes/api.py
from flask import Blueprint, jsonify
from app.utils.db import db, TrafficLog

api_bp = Blueprint('api', __name__)

@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok"})

@api_bp.route('/chart_data', methods=['GET'])
def chart_data():
    """
    DBから最新のパケット情報を取得して返すAPI
    例として最新20件の {timestamp, packet_length} を返す
    """
    # 最新20件
    logs = TrafficLog.query.order_by(TrafficLog.id.desc()).limit(20).all()
    # 時間順に並び替え
    logs = logs[::-1]

    data = []
    for log in logs:
        data.append({
            "timestamp": log.timestamp,
            "packet_length": log.packet_length or 0
        })
    return jsonify(data)
