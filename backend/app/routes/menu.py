from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from sqlalchemy import desc
from app import db
from app.models.user import User
from app.models.meal import Meal, Menu

menus_bp = Blueprint('menus', __name__)


def paginate_query(query, page, per_page):
    """Helper function to paginate SQLAlchemy queries"""
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def validate_menu_data(data, is_update=False):
    """Validate menu data and return (is_valid, error_message)"""
    errors = []

    if not is_update:
        if 'date' not in data:
            errors.append('date is required')
        if 'meal_ids' not in data:
            errors.append('meal_ids is required')

    if 'date' in data:
        try:
            date.fromisoformat(data['date'])
        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD')

    if 'meal_ids' in data:
        if not isinstance(data['meal_ids'], list):
            errors.append('meal_ids must be an array')
        elif len(data['meal_ids']) == 0:
            errors.append('meal_ids must not be empty')
        else:
            for meal_id in data['meal_ids']:
                try:
                    if int(meal_id) <= 0:
                        errors.append('All meal_ids must be positive integers')
                        break
                except (ValueError, TypeError):
                    errors.append('All meal_ids must be valid integers')
                    break

    return len(errors) == 0, errors


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
    is_valid, errors = validate_menu_data(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    menu_date_str = data.get('date')       # expected: "YYYY-MM-DD"
    meal_ids = data.get('meal_ids', [])    # list of meal IDs to include

    menu_date = date.fromisoformat(menu_date_str)

    # Only one menu allowed per day
    if Menu.query.filter_by(date=menu_date).first():
        return jsonify({'error': f'A menu for {menu_date_str} already exists'}), 409

    meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
    if len(meals) != len(meal_ids):
        return jsonify({'error': 'Some meal_ids are invalid'}), 404

    menu = Menu(date=menu_date, created_by=user.id, meals=meals)
    db.session.add(menu)
    db.session.commit()

    return jsonify({'message': 'Menu created', 'menu': menu.to_dict()}), 201


# ── GET /menus  — list all menus (any authenticated user) ───────────────────
@menus_bp.route('', methods=['GET'])
@jwt_required()
def get_menus():
    # Parse pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        return jsonify({'error': 'page and per_page must be integers'}), 400

    # Parse date filter
    date_filter = request.args.get('date')
    query = Menu.query

    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter_by(date=filter_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    query = query.order_by(desc(Menu.date))

    result = paginate_query(query, page, per_page)

    return jsonify({
        'menus': [m.to_dict() for m in result['items']],
        'pagination': result['pagination']
    }), 200


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

    is_valid, errors = validate_menu_data(data, is_update=True)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    if 'date' in data:
        new_date = date.fromisoformat(data['date'])
        # Check uniqueness only if date is actually changing
        if new_date != menu.date and Menu.query.filter_by(date=new_date).first():
            return jsonify({'error': f'A menu for {data["date"]} already exists'}), 409
        menu.date = new_date

    if 'meal_ids' in data:
        meals = Meal.query.filter(Meal.id.in_(data['meal_ids'])).all()
        if len(meals) != len(data['meal_ids']):
            return jsonify({'error': 'Some meal_ids are invalid'}), 404
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