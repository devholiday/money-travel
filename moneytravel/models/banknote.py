from datetime import datetime
from moneytravel import db

class Banknote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iso_code = db.Column(db.String(3), nullable=False)
    number = db.Column(db.String(255), nullable=False)
    denomination = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,  default=datetime.utcnow)
    comments = db.relationship('Comment', backref='banknote', lazy=True)

    def __repr__(self):
        return f"Banknote('{self.iso_code}','{self.number}','{self.denomination}')"