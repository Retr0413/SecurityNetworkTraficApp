from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TrafficLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    detail = db.Column(db.Text)