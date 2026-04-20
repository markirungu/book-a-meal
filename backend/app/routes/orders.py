from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.caterer import Caterer
from app.models.meals import Meal, Menu
from app.models.order import Order
from app.models.refund import Refund
from app.models.user import User
from app.utils.validators import parse_int, paginate_query

orders_bp = Blueprint('orders', __name__)
ALLOWED_STATUSES = {'pending', 'preparing', 'completed', 'cancelled', 'guest_order'}


def current_user():
    uid = get_jwt_identity()
    return User.query.get(uid)


def serialize_trends(caterer_id):
    rows = db.session.query(Meal.name, db.func.count(Order.id).label('count')) \
        .join(Order, Order.meal_id == Meal.id) \
        .filter(Order.caterer_id == caterer_id) \
        .group_by(Meal.name) \
        .order_by(db.desc('count')) \
        .limit(5) \
        .all()
    return [{'meal_name': name, 'orders': count} for name, count in rows]


@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    meal_id = parse_int(data.get('meal_id'))
    menu_id = parse_int(data.get('menu_id'))
    quantity = parse_int(data.get('quantity'), default=1, minimum=1, maximum=20) or 1

    if not meal_id or not menu_id:
        return jsonify({'error': 'meal_id and menu_id are required'}), 400

    menu = Menu.query.get(menu_id)
    meal = Meal.query.get(meal_id)
    if not menu or not meal:
        return jsonify({'error': 'Menu or meal not found'}), 404

    if not menu.is_published:
        return jsonify({'error': 'Menu is not published'}), 400

    if menu.cutoff_time and datetime.utcnow() > menu.cutoff_time:
        return jsonify({'error': 'Order cutoff time has passed'}), 400

    if meal.id not in [m.id for m in menu.meals]:
        return jsonify({'error': 'Meal is not available in this menu'}), 400

    order = Order(
        customer_id=user.id,
        caterer_id=menu.caterer_id,
        menu_id=menu.id,
        meal_id=meal.id,
        quantity=quantity,
        unit_price=meal.price,
        notes=data.get('notes')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order placed', 'order': order.to_dict()}), 201


@orders_bp.route('/guest', methods=['POST'])
def create_guest_order():
    data = request.get_json() or {}
    meal_id = parse_int(data.get('meal_id'))
    menu_id = parse_int(data.get('menu_id'))
    quantity = parse_int(data.get('quantity'), default=1, minimum=1, maximum=20) or 1

    guest_name = (data.get('guest_name') or '').strip()
    guest_email = (data.get('guest_email') or '').strip().lower()
    guest_phone = (data.get('guest_phone') or '').strip()
    delivery_info = (data.get('delivery_info') or '').strip()

    if not meal_id or not menu_id:
        return jsonify({'error': 'meal_id and menu_id are required'}), 400

    if not guest_name or not guest_email or not guest_phone:
        return jsonify({'error': 'guest_name, guest_email and guest_phone are required'}), 400

    menu = Menu.query.get(menu_id)
    meal = Meal.query.get(meal_id)
    if not menu or not meal:
        return jsonify({'error': 'Menu or meal not found'}), 404

    if not menu.is_published:
        return jsonify({'error': 'Menu is not published'}), 400

    if menu.cutoff_time and datetime.utcnow() > menu.cutoff_time:
        return jsonify({'error': 'Order cutoff time has passed'}), 400

    if meal.id not in [m.id for m in menu.meals]:
        return jsonify({'error': 'Meal is not available in this menu'}), 400

    order = Order(
        customer_id=None,
        caterer_id=menu.caterer_id,
        menu_id=menu.id,
        meal_id=meal.id,
        quantity=quantity,
        unit_price=meal.price,
        status='guest_order',
        guest_name=guest_name,
        guest_email=guest_email,
        guest_phone=guest_phone,
        delivery_info=delivery_info or None,
        notes=data.get('notes'),
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Guest order created', 'order': order.to_dict()}), 201


@orders_bp.route('', methods=['GET'])
@jwt_required()
def list_orders():
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    page = parse_int(request.args.get('page'), default=1, minimum=1) or 1
    per_page = parse_int(request.args.get('per_page'), default=10, minimum=1, maximum=100) or 10

    query = Order.query
    if user.role == 'customer':
        query = query.filter_by(customer_id=user.id)
    elif user.role == 'admin':
        query = query.filter_by(caterer_id=user.caterer_id)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    paged = paginate_query(query.order_by(Order.created_at.desc()), page, per_page)
    return jsonify({'data': [o.to_dict() for o in paged['items']], 'meta': paged['meta']}), 200


@orders_bp.route('/active', methods=['GET'])
@jwt_required()
def active_order():
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.filter_by(customer_id=user.id).filter(Order.status.in_(['pending', 'preparing'])).order_by(Order.created_at.desc()).first()
    if not order:
        return jsonify({'data': None}), 200
    return jsonify({'data': order.to_dict()}), 200


@orders_bp.route('/history', methods=['GET'])
@jwt_required()
def order_history():
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    page = parse_int(request.args.get('page'), default=1, minimum=1) or 1
    per_page = parse_int(request.args.get('per_page'), default=10, minimum=1, maximum=100) or 10

    query = Order.query
    if user.role == 'customer':
        query = query.filter_by(customer_id=user.id)
    elif user.role == 'admin':
        query = query.filter_by(caterer_id=user.caterer_id)

    paged = paginate_query(query.order_by(Order.created_at.desc()), page, per_page)
    return jsonify({'data': [o.to_dict() for o in paged['items']], 'meta': paged['meta']}), 200


@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}

    if user.role == 'customer':
        if order.customer_id != user.id:
            return jsonify({'error': 'Forbidden'}), 403
        if order.status not in ['pending']:
            return jsonify({'error': 'Order cannot be modified now'}), 400
        if order.menu and order.menu.cutoff_time and datetime.utcnow() > order.menu.cutoff_time:
            return jsonify({'error': 'Cutoff time has passed'}), 400

        new_meal_id = parse_int(data.get('meal_id'))
        if new_meal_id:
            meal = Meal.query.get(new_meal_id)
            if not meal:
                return jsonify({'error': 'Meal not found'}), 404
            if meal.id not in [m.id for m in order.menu.meals]:
                return jsonify({'error': 'Meal is not available in this menu'}), 400
            order.meal_id = meal.id
            order.unit_price = meal.price

        if data.get('quantity') is not None:
            quantity = parse_int(data.get('quantity'), minimum=1, maximum=20)
            if not quantity:
                return jsonify({'error': 'quantity must be between 1 and 20'}), 400
            order.quantity = quantity

    elif user.role == 'admin':
        if order.caterer_id != user.caterer_id:
            return jsonify({'error': 'Forbidden'}), 403
        new_status = data.get('status')
        if new_status and new_status not in ALLOWED_STATUSES:
            return jsonify({'error': 'Invalid status'}), 400
        if new_status:
            order.status = new_status
            if new_status == 'completed':
                order.fulfilled_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Order updated', 'order': order.to_dict()}), 200


@orders_bp.route('/<int:order_id>/refund', methods=['POST'])
@jwt_required()
def refund_order(order_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.get_or_404(order_id)
    if user.role == 'customer' and order.customer_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403
    if user.role == 'admin' and order.caterer_id != user.caterer_id:
        return jsonify({'error': 'Forbidden'}), 403

    payload = request.get_json() or {}
    penalty = payload.get('penalty_percent', 10.0)
    try:
        penalty = max(0.0, min(100.0, float(penalty)))
    except (TypeError, ValueError):
        return jsonify({'error': 'penalty_percent must be numeric'}), 400

    gross = order.total_price
    penalty_amount = round((penalty / 100.0) * gross, 2)
    net = round(gross - penalty_amount, 2)

    refund = Refund(
        order_id=order.id,
        requested_by=user.id,
        penalty_percent=penalty,
        gross_amount=gross,
        penalty_amount=penalty_amount,
        net_amount=net,
        reason=payload.get('reason'),
    )

    order.status = 'cancelled'
    db.session.add(refund)
    db.session.commit()

    return jsonify({'message': 'Refund processed', 'refund': refund.to_dict()}), 201


@orders_bp.route('/admin/revenue', methods=['GET'])
@jwt_required()
def admin_revenue():
    user = current_user()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    query = Order.query.filter_by(caterer_id=user.caterer_id)
    if request.args.get('fulfilled_only', 'true').lower() == 'true':
        query = query.filter_by(status='completed')

    total = sum(order.total_price for order in query.all())
    return jsonify({'data': {'total_revenue': round(total, 2), 'fulfilled_only': request.args.get('fulfilled_only', 'true').lower() == 'true'}}), 200


@orders_bp.route('/admin/analytics', methods=['GET'])
@jwt_required()
def admin_analytics():
    user = current_user()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    trends = serialize_trends(user.caterer_id)
    by_day = db.session.query(
        db.func.date(Order.created_at).label('day'),
        db.func.count(Order.id).label('count')
    ).filter_by(caterer_id=user.caterer_id).group_by(db.func.date(Order.created_at)).order_by(db.func.date(Order.created_at).desc()).limit(14).all()

    return jsonify({
        'data': {
            'top_meals': trends,
            'peak_days': [{'day': str(day), 'orders': count} for day, count in by_day],
        }
    }), 200
