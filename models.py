from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer = db.Column(db.String(100))

    total = db.Column(db.Float)

    created_at = db.Column(db.String(50))