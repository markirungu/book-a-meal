from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from app import db
from app.models.user import User
from app.models.meal import Meal, Menu

menus_bp = Blueprint('menus', __name__)


# ── helper: guard admin-only endpoints ──────────────────────────────────────
def admin_required():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


# ── POST /menus  — admin creates/sets menu for a day ────────────────────────
@menus_bp.route('', methods=['POST'])
@jwt_required()
def create_menu():
    user, err = admin_required()
    if err:
        return err

    data = request.get_json()
    menu_date_str = data.get('date')       # expected: "YYYY-MM-DD"
    meal_ids = data.get('meal_ids', [])    # list of meal IDs to include

    if not menu_date_str:
        return jsonify({'error': 'date is required (YYYY-MM-DD)'}), 400
    if not meal_ids:
        return jsonify({'error': 'meal_ids must not be empty'}), 400

    try:
        menu_date = date.fromisoformat(menu_date_str)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Only one menu allowed per day
    if Menu.query.filter_by(date=menu_date).first():
        return jsonify({'error': f'A menu for {menu_date_str} already exists'}), 409

    meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
    if not meals:
        return jsonify({'error': 'No valid meals found for the given meal_ids'}), 404

    menu = Menu(date=menu_date, created_by=user.id, meals=meals)
    db.session.add(menu)
    db.session.commit()

    return jsonify({'message': 'Menu created', 'menu': menu.to_dict()}), 201


# ── GET /menus  — list all menus (any authenticated user) ───────────────────
@menus_bp.route('', methods=['GET'])
@jwt_required()
def get_menus():
    menus = Menu.query.order_by(Menu.date.desc()).all()
    return jsonify([m.to_dict() for m in menus]), 200


# ── GET /menus/today  — today's menu (shortcut for customers) ───────────────
@menus_bp.route('/today', methods=['GET'])
@jwt_required()
def get_todays_menu():
    menu = Menu.query.filter_by(date=date.today()).first()
    if not menu:
        return jsonify({'error': 'No menu set for today'}), 404
    return jsonify(menu.to_dict()), 200


# ── GET /menus/<id>  — single menu by ID ────────────────────────────────────
@menus_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()
def get_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    return jsonify(menu.to_dict()), 200


# ── PUT /menus/<id>  — admin updates a menu (swap meals or change date) ─────
@menus_bp.route('/<int:menu_id>', methods=['PUT'])
@jwt_required()
def update_menu(menu_id):
    user, err = admin_required()
    if err:
        return err

    menu = Menu.query.get_or_404(menu_id)
    data = request.get_json()

    if 'date' in data:
        try:
            new_date = date.fromisoformat(data['date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        # Check uniqueness only if date is actually changing
        if new_date != menu.date and Menu.query.filter_by(date=new_date).first():
            return jsonify({'error': f'A menu for {data["date"]} already exists'}), 409
        menu.date = new_date

    if 'meal_ids' in data:
        meals = Meal.query.filter(Meal.id.in_(data['meal_ids'])).all()
        if not meals:
            return jsonify({'error': 'No valid meals found for the given meal_ids'}), 404
        menu.meals = meals

    db.session.commit()
    return jsonify({'message': 'Menu updated', 'menu': menu.to_dict()}), 200


# ── DELETE /menus/<id>  — admin deletes a menu ──────────────────────────────
@menus_bp.route('/<int:menu_id>', methods=['DELETE'])
@jwt_required()
def delete_menu(menu_id):
    user, err = admin_required()
    if err:
        return err

    menu = Menu.query.get_or_404(menu_id)
    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': 'Menu deleted'}), 200