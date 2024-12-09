from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Traffic(id.Model):
    id = db.column(db.Integer, primary_key=True)
    label = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    detail = db.Column(db.Text)