from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load default config
    app.config.from_object("app.config.Config")
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Force SQLite if TESTING is True
    if app.config.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import user
        from app.models import meals
        from app.routes.auth import auth_bp
        from app.routes.meals import meals_bp
        from app.routes.menu import menus_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(meals_bp, url_prefix='/meals')
        app.register_blueprint(menus_bp, url_prefix='/menus')

    @app.route("/")
    def index():
        return {"message": "Book-A-Meal API is running"}, 200

    return app