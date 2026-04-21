from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from sqlalchemy import desc
from app import db
from app.models.user import User
from app.models.meals import Meal, Menu, MenuItem
from app.models.notification import Notification
from app.utils.validators import parse_int, parse_iso_date, parse_iso_datetime

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
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': total_pages
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
    
    # Use person3's validation (more thorough)
    is_valid, errors = validate_menu_data(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    menu_date_str = data.get('date')
    meal_ids = data.get('meal_ids', [])
    special_meal_ids = set(data.get('special_meal_ids', []))

    menu_date = date.fromisoformat(menu_date_str)

    existing = Menu.query.filter_by(date=menu_date, caterer_id=user.caterer_id).first()
    if existing:
        return jsonify({'error': f'A menu for {menu_date_str} already exists'}), 409

    meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
    if len(meals) != len(meal_ids):
        return jsonify({'error': 'Some meal_ids are invalid'}), 404

    cutoff_time = parse_iso_datetime(data.get('cutoff_time')) if data.get('cutoff_time') else None

    menu = Menu(
        date=menu_date,
        created_by=user.id,
        caterer_id=user.caterer_id,
        cutoff_time=cutoff_time,
        is_published=bool(data.get('is_published', True)),
    )
    db.session.add(menu)

    db.session.flush()
    for meal in meals:
        db.session.add(MenuItem(menu_id=menu.id, meal_id=meal.id, is_special=meal.id in special_meal_ids))

    # ✅ YOUR NOTIFICATION CODE - KEPT!
    if menu.is_published:
        customers = User.query.filter_by(role='customer').all()
        for customer in customers:
            db.session.add(Notification(
                user_id=customer.id,
                title='Daily Menu Published 🍽️',
                message=f'The menu for {menu.date.isoformat()} is now available. Check out today\'s specials!',
                notification_type='menu',
            ))

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

    # Filter by caterer
    caterer_id = parse_int(request.args.get('caterer_id'))
    if caterer_id:
        query = query.filter_by(caterer_id=caterer_id)

    query = query.order_by(desc(Menu.date))

    result = paginate_query(query, page, per_page)

    return jsonify({
        'data': [m.to_dict() for m in result['items']],
        'meta': result['meta']
    }), 200


# ── GET /menus/today  — today's menu (shortcut for customers) ───────────────
@menus_bp.route('/today', methods=['GET'])
@jwt_required()
def get_todays_menu():
    caterer_id = parse_int(request.args.get('caterer_id'))
    query = Menu.query.filter_by(date=date.today(), is_published=True)
    if caterer_id:
        query = query.filter_by(caterer_id=caterer_id)
    menu = query.first()
    if not menu:
        return jsonify({'error': 'No menu set for today'}), 404
    return jsonify(menu.to_dict()), 200


# ── GET /menus/<id>  — single menu by ID ────────────────────────────────────
@menus_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()
def get_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    return jsonify(menu.to_dict()), 200


# ── PUT /menus/<id>  — admin updates a menu ─────────────────────────────────
@menus_bp.route('/<int:menu_id>', methods=['PUT'])
@jwt_required()
def update_menu(menu_id):
    user, err = admin_required()
    if err:
        return err

    menu = Menu.query.get_or_404(menu_id)
    if menu.caterer_id and user.caterer_id and menu.caterer_id != user.caterer_id:
        return jsonify({'error': 'Cannot modify another caterer\'s menu'}), 403

    data = request.get_json()

    is_valid, errors = validate_menu_data(data, is_update=True)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    if 'date' in data:
        new_date = date.fromisoformat(data['date'])
        # Check uniqueness only if date is actually changing
        existing = Menu.query.filter_by(date=new_date, caterer_id=menu.caterer_id).first()
        if new_date != menu.date and existing:
            return jsonify({'error': f'A menu for {data["date"]} already exists'}), 409
        menu.date = new_date

    if 'cutoff_time' in data:
        cutoff = parse_iso_datetime(data.get('cutoff_time')) if data.get('cutoff_time') else None
        menu.cutoff_time = cutoff

    if 'is_published' in data:
        was_published = menu.is_published
        menu.is_published = bool(data.get('is_published'))
        
        # ✅ YOUR NOTIFICATION CODE - Send if newly published
        if menu.is_published and not was_published:
            customers = User.query.filter_by(role='customer').all()
            for customer in customers:
                db.session.add(Notification(
                    user_id=customer.id,
                    title='Menu Updated 🔄',
                    message=f'The menu for {menu.date.isoformat()} has been updated. Check out the changes!',
                    notification_type='menu',
                ))

    if 'meal_ids' in data:
        meal_ids = data.get('meal_ids', [])
        special_meal_ids = set(data.get('special_meal_ids', []))
        meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
        if len(meals) != len(meal_ids):
            return jsonify({'error': 'Some meal_ids are invalid'}), 404
        MenuItem.query.filter_by(menu_id=menu.id).delete()
        for meal in meals:
            db.session.add(MenuItem(menu_id=menu.id, meal_id=meal.id, is_special=meal.id in special_meal_ids))

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
    if menu.caterer_id and user.caterer_id and menu.caterer_id != user.caterer_id:
        return jsonify({'error': 'Cannot delete another caterer\'s menu'}), 403

    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': 'Menu deleted'}), 200