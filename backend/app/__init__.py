from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    mail.init_app(app)

    with app.app_context():
        from app.models import user
        from app.models import meal  # registers Meal, Menu, menu_meals with SQLAlchemy
        from app.models import order  # registers Order with SQLAlchemy
        from app.routes.auth import auth_bp
        from app.routes.meals import meals_bp
        from app.routes.menu import menus_bp
        from app.routes.orders import orders_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(meals_bp, url_prefix='/meals')
        app.register_blueprint(menus_bp, url_prefix='/menus')
        app.register_blueprint(orders_bp, url_prefix='/orders')

    @app.route("/")
    def index():
        return {"message": "Book-A-Meal API is running"}, 200

    return app