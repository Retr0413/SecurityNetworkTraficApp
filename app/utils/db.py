from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TrafficLog(db.Model):
    __tablename__ = 'traffic_log'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    src_ip = db.Column(db.String(50))
    dst_ip = db.Column(db.String(50))
    protocol = db.Column(db.Integer)
    packet_length = db.Column(db.Integer)
    ttl = db.Column(db.Integer)
    flags = db.Column(db.String(10))
    src_port = db.Column(db.Integer)
    dst_port = db.Column(db.Integer)
    label = db.Column(db.String(50), nullable=True)
    processed = db.Column(db.Boolean, default=False)
