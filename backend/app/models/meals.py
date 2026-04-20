from app import db
from datetime import datetime


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    is_special = db.Column(db.Boolean, default=False, nullable=False)

    meal = db.relationship('Meal', backref=db.backref('menu_links', lazy=True))

    def to_dict(self):
        payload = self.meal.to_dict() if self.meal else {}
        payload['is_special'] = self.is_special
        return payload


class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    caterer_id = db.Column(db.Integer, db.ForeignKey('caterers.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    recipe_source = db.Column(db.String(64), nullable=True)
    ingredients = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'caterer_id': self.caterer_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'recipe_source': self.recipe_source,
            'ingredients': self.ingredients or [],
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Meal {self.name}>'


class Menu(db.Model):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    caterer_id = db.Column(db.Integer, db.ForeignKey('caterers.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cutoff_time = db.Column(db.DateTime, nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    menu_items = db.relationship('MenuItem', lazy='subquery', cascade='all, delete-orphan', backref='menu')

    @property
    def meals(self):
        return [item.meal for item in self.menu_items if item.meal]

    @property
    def special_meals(self):
        return [item.meal for item in self.menu_items if item.is_special and item.meal]

    def to_dict(self):
        return {
            'id': self.id,
            'caterer_id': self.caterer_id,
            'date': self.date.isoformat(),
            'created_by': self.created_by,
            'is_published': self.is_published,
            'cutoff_time': self.cutoff_time.isoformat() if self.cutoff_time else None,
            'meals': [item.to_dict() for item in self.menu_items],
            'special_meals': [meal.to_dict() for meal in self.special_meals],
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<Menu {self.date}>'