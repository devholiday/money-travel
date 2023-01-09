from datetime import datetime
from moneytravel import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"


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


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,  default=datetime.utcnow)
    enabled = db.Column(db.Boolean, nullable=False,  default=False)
    banknote_id = db.Column(db.Integer, db.ForeignKey('banknote.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.city}','{self.address}','{self.created_at}')"
