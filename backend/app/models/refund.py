from datetime import datetime
from app import db


class Refund(db.Model):
    __tablename__ = 'refunds'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    penalty_percent = db.Column(db.Float, nullable=False, default=10.0)
    gross_amount = db.Column(db.Float, nullable=False)
    penalty_amount = db.Column(db.Float, nullable=False)
    net_amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref=db.backref('refunds', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'requested_by': self.requested_by,
            'penalty_percent': self.penalty_percent,
            'gross_amount': self.gross_amount,
            'penalty_amount': self.penalty_amount,
            'net_amount': self.net_amount,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
