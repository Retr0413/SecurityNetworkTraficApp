from flask import Blueprint, render_template
from app.utils.db import db, TrafficLog

front_bp = Blueprint('front', __name__)

@front_bp.route('/')
def index():
    logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).limit(50).all()
    labels = [l.label for l in logs]
    from collections import Counter
    cnt = Counter(labels)
    return render_template('index.html', counts=cnt)

@front_bp.route('/logs')
def show_logs():
    Logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).all()
    return render_template('logs.html', logs=Logs)