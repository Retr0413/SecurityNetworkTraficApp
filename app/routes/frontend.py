from flask import Blueprint, render_template
from app.utils.db import db, TrafficLog

front_bp = Blueprint('frontend', __name__)

@front_bp.route('/')
def index():
    logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).limit(50).all()
    return render_template('index.html', logs=logs)
