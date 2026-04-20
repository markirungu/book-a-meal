from datetime import datetime
from app import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    caterer_id = db.Column(db.Integer, db.ForeignKey('caterers.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    notes = db.Column(db.String(255), nullable=True)
    guest_name = db.Column(db.String(120), nullable=True)
    guest_email = db.Column(db.String(120), nullable=True)
    guest_phone = db.Column(db.String(40), nullable=True)
    delivery_info = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fulfilled_at = db.Column(db.DateTime, nullable=True)

    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_orders', lazy=True))
    meal = db.relationship('Meal', backref=db.backref('orders', lazy=True))
    menu = db.relationship('Menu', backref=db.backref('orders', lazy=True))

    @property
    def total_price(self):
        return round(self.unit_price * self.quantity, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'caterer_id': self.caterer_id,
            'menu_id': self.menu_id,
            'meal_id': self.meal_id,
            'meal_name': self.meal.name if self.meal else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'status': self.status,
            'notes': self.notes,
            'is_guest_order': self.customer_id is None,
            'guest_name': self.guest_name,
            'guest_email': self.guest_email,
            'guest_phone': self.guest_phone,
            'delivery_info': self.delivery_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'fulfilled_at': self.fulfilled_at.isoformat() if self.fulfilled_at else None,
        }
