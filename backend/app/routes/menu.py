from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from app import db
from app.models.user import User
from app.models.meals import Meal, Menu, MenuItem
from app.models.notification import Notification
from app.utils.validators import parse_int, parse_iso_date, parse_iso_datetime, paginate_query

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
    menu_date_str = data.get('date')
    meal_ids = data.get('meal_ids', [])
    special_meal_ids = set(data.get('special_meal_ids', []))

    if not menu_date_str:
        return jsonify({'error': 'date is required (YYYY-MM-DD)'}), 400
    if not meal_ids:
        return jsonify({'error': 'meal_ids must not be empty'}), 400

    menu_date = parse_iso_date(menu_date_str)
    if not menu_date:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    existing = Menu.query.filter_by(date=menu_date, caterer_id=user.caterer_id).first()
    if existing:
        return jsonify({'error': f'A menu for {menu_date_str} already exists'}), 409

    meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
    if len(meals) != len(meal_ids):
        return jsonify({'error': 'No valid meals found for the given meal_ids'}), 404

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

    if menu.is_published:
        customers = User.query.filter_by(role='customer').all()
        for customer in customers:
            db.session.add(Notification(
                user_id=customer.id,
                title='Daily Menu Published',
                message=f'New menu for {menu.date.isoformat()} is now available.',
                notification_type='menu',
            ))

    db.session.commit()

    return jsonify({'message': 'Menu created', 'menu': menu.to_dict()}), 201


# ── GET /menus  — list all menus (any authenticated user) ───────────────────
@menus_bp.route('', methods=['GET'])
@jwt_required()
def get_menus():
    page = parse_int(request.args.get('page'), default=1, minimum=1) or 1
    per_page = parse_int(request.args.get('per_page'), default=10, minimum=1, maximum=100) or 10
    query = Menu.query

    menu_date = parse_iso_date(request.args.get('date')) if request.args.get('date') else None
    if menu_date:
        query = query.filter_by(date=menu_date)

    caterer_id = parse_int(request.args.get('caterer_id'))
    if caterer_id:
        query = query.filter_by(caterer_id=caterer_id)

    paged = paginate_query(query.order_by(Menu.date.desc()), page, per_page)
    return jsonify({'data': [m.to_dict() for m in paged['items']], 'meta': paged['meta']}), 200


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

    if 'date' in data:
        new_date = parse_iso_date(data['date'])
        if not new_date:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        existing = Menu.query.filter_by(date=new_date, caterer_id=menu.caterer_id).first()
        if new_date != menu.date and existing:
            return jsonify({'error': f'A menu for {data["date"]} already exists'}), 409
        menu.date = new_date

    if 'cutoff_time' in data:
        cutoff = parse_iso_datetime(data.get('cutoff_time')) if data.get('cutoff_time') else None
        if data.get('cutoff_time') and not cutoff:
            return jsonify({'error': 'Invalid cutoff_time format. Use ISO datetime'}), 400
        menu.cutoff_time = cutoff

    if 'is_published' in data:
        menu.is_published = bool(data.get('is_published'))

    if 'meal_ids' in data:
        meal_ids = data.get('meal_ids') or []
        special_meal_ids = set(data.get('special_meal_ids', []))
        meals = Meal.query.filter(Meal.id.in_(meal_ids)).all()
        if len(meals) != len(meal_ids):
            return jsonify({'error': 'No valid meals found for the given meal_ids'}), 404
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