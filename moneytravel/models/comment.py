from datetime import datetime
from moneytravel import db

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
