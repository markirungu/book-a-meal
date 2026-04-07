from app import db
from datetime import datetime

# Association table — links meals to menus (many-to-many)
menu_meals = db.Table(
    'menu_meals',
    db.Column('menu_id', db.Integer, db.ForeignKey('menus.id'), primary_key=True),
    db.Column('meal_id', db.Integer, db.ForeignKey('meals.id'), primary_key=True)
)


class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Meal {self.name}>'


class Menu(db.Model):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)   # one menu per day
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Many-to-many: a menu contains many meals
    meals = db.relationship('Meal', secondary=menu_meals, lazy='subquery',
                            backref=db.backref('menus', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'created_by': self.created_by,
            'meals': [meal.to_dict() for meal in self.meals],
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Menu {self.date}>'