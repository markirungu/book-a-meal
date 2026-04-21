from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
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
    CORS(app, origins=[
        'http://localhost:5173',
        'http://localhost:5174',
        'https://book-a-meal-gray.vercel.app',
        'https://book-a-meal.vercel.app'
    ])
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import user
        from app.models import order
        from app.models import caterer
        from app.models import meals
        from app.models import refund
        from app.models import notification
        
        from app.routes.auth import auth_bp
        from app.routes.caterers import caterers_bp
        from app.routes.meals import meals_bp
        from app.routes.menu import menus_bp
        from app.routes.orders import orders_bp
        from app.routes.notifications import notifications_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(caterers_bp, url_prefix='/caterers')
        app.register_blueprint(meals_bp, url_prefix='/meals')
        app.register_blueprint(menus_bp, url_prefix='/menus')
        app.register_blueprint(orders_bp, url_prefix='/orders')
        app.register_blueprint(notifications_bp, url_prefix='/notifications')

    @app.route("/")
    def index():
        return {"message": "Book-A-Meal API is running"}, 200

    @app.route("/setup-db", methods=["GET"])
    def setup_db():
        try:
            db.drop_all()
            db.create_all()
            return {"message": "Database tables dropped and recreated successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @app.route("/fix-caterer", methods=["GET"])
    @jwt_required()
    def fix_caterer():
        from app.models.caterer import Caterer
        from app.models.user import User
        from app.models.meals import Menu
        
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Create caterer if needed (with correct fields)
        if not user.caterer_id:
            caterer = Caterer(
                name=f"{user.name}'s Kitchen",
                description="Main kitchen for Book-A-Meal",
                owner_user_id=user.id
            )
            db.session.add(caterer)
            db.session.flush()
            user.caterer_id = caterer.id
        
        # Fix any menus without caterer
        menus = Menu.query.filter_by(caterer_id=None).all()
        for menu in menus:
            menu.caterer_id = user.caterer_id
        
        db.session.commit()
        
        return {
            "message": "Caterer fixed", 
            "caterer_id": user.caterer_id, 
            "menus_updated": len(menus)
        }, 200

    return app