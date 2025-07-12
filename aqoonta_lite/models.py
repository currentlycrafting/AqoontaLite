from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    lesson = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)