from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, datetime
from sqlalchemy import desc
from app import db
from app.models.user import User
from app.models.order import Order
from app.models.meal import Meal, Menu

orders_bp = Blueprint('orders', __name__)


def validate_order_data(data, is_update=False):
    """Validate order data and return (is_valid, error_message)"""
    errors = []

    if not is_update:
        if 'meal_id' not in data:
            errors.append('meal_id is required')
        if 'quantity' not in data:
            errors.append('quantity is required')

    if 'meal_id' in data:
        try:
            meal_id = int(data['meal_id'])
            if meal_id <= 0:
                errors.append('meal_id must be a positive integer')
        except (ValueError, TypeError):
            errors.append('meal_id must be a valid integer')

    if 'quantity' in data:
        try:
            quantity = int(data['quantity'])
            if quantity <= 0:
                errors.append('quantity must be a positive integer')
            if quantity > 10:
                errors.append('quantity cannot exceed 10')
        except (ValueError, TypeError):
            errors.append('quantity must be a valid integer')

    if 'status' in data and data['status'] not in ['pending', 'confirmed', 'cancelled', 'fulfilled']:
        errors.append('status must be one of: pending, confirmed, cancelled, fulfilled')

    return len(errors) == 0, errors


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


# ── POST /orders  — customer places an order ────────────────────────────────
@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    is_valid, errors = validate_order_data(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    meal_id = data['meal_id']
    quantity = data.get('quantity', 1)

    # Check if meal exists
    meal = Meal.query.get(meal_id)
    if not meal:
        return jsonify({'error': 'Meal not found'}), 404

    # Check if meal is available today (in today's menu)
    today = date.today()
    todays_menu = Menu.query.filter_by(date=today).first()
    if not todays_menu or meal not in todays_menu.meals:
        return jsonify({'error': 'Meal is not available in today\'s menu'}), 400

    # Check if user already has a pending/confirmed order for this meal today
    existing_order = Order.query.filter_by(
        user_id=user_id,
        meal_id=meal_id,
        order_date=today
    ).filter(Order.status.in_(['pending', 'confirmed'])).first()

    if existing_order:
        return jsonify({'error': 'You already have an active order for this meal today'}), 409

    order = Order(
        user_id=user_id,
        meal_id=meal_id,
        quantity=quantity,
        order_date=today
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({'message': 'Order placed successfully', 'order': order.to_dict()}), 201


# ── GET /orders  — list orders (admin: all, customer: own) ───────────────────
@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Parse pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        return jsonify({'error': 'page and per_page must be integers'}), 400

    # Parse filters
    status_filter = request.args.get('status')
    date_filter = request.args.get('date')
    meal_id_filter = request.args.get('meal_id')

    query = Order.query

    # Apply filters
    if status_filter:
        if status_filter not in ['pending', 'confirmed', 'cancelled', 'fulfilled']:
            return jsonify({'error': 'Invalid status filter'}), 400
        query = query.filter_by(status=status_filter)

    if date_filter:
        try:
            filter_date = date.fromisoformat(date_filter)
            query = query.filter_by(order_date=filter_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    if meal_id_filter:
        try:
            meal_id = int(meal_id_filter)
            query = query.filter_by(meal_id=meal_id)
        except ValueError:
            return jsonify({'error': 'meal_id must be a valid integer'}), 400

    # Apply user filter (customers only see their own orders)
    if user.role != 'admin':
        query = query.filter_by(user_id=user_id)

    # Order by creation date (newest first)
    query = query.order_by(desc(Order.created_at))

    result = paginate_query(query, page, per_page)

    return jsonify({
        'orders': [order.to_dict() for order in result['items']],
        'pagination': result['pagination']
    }), 200


# ── GET /orders/<id>  — single order ─────────────────────────────────────────
@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.get_or_404(order_id)

    # Customers can only view their own orders
    if user.role != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    return jsonify(order.to_dict()), 200


# ── PUT /orders/<id>  — update order (customer: change meal/quantity, admin: status) ──
@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.get_or_404(order_id)

    # Customers can only update their own orders
    if user.role != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    is_valid, errors = validate_order_data(data, is_update=True)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    # Customers can only update meal_id and quantity, and only if order is pending
    if user.role != 'admin':
        if order.status != 'pending':
            return jsonify({'error': 'Can only update pending orders'}), 400

        allowed_fields = ['meal_id', 'quantity']
        for key in data:
            if key not in allowed_fields:
                return jsonify({'error': f'Customers can only update: {", ".join(allowed_fields)}'}), 400

        # If changing meal, validate it's available today
        if 'meal_id' in data:
            meal_id = data['meal_id']
            meal = Meal.query.get(meal_id)
            if not meal:
                return jsonify({'error': 'Meal not found'}), 404

            today = date.today()
            todays_menu = Menu.query.filter_by(date=today).first()
            if not todays_menu or meal not in todays_menu.meals:
                return jsonify({'error': 'Meal is not available in today\'s menu'}), 400

    # Apply updates
    if 'meal_id' in data:
        order.meal_id = data['meal_id']
    if 'quantity' in data:
        order.quantity = data['quantity']
    if 'status' in data and user.role == 'admin':
        order.status = data['status']

    db.session.commit()

    return jsonify({'message': 'Order updated successfully', 'order': order.to_dict()}), 200


# ── DELETE /orders/<id>  — cancel order ──────────────────────────────────────
@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    order = Order.query.get_or_404(order_id)

    # Customers can only cancel their own orders
    if user.role != 'admin' and order.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403

    # Only allow cancellation of pending orders
    if order.status != 'pending':
        return jsonify({'error': 'Can only cancel pending orders'}), 400

    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Order cancelled successfully'}), 200


# ── GET /orders/history  — customer order history ───────────────────────────
@orders_bp.route('/history', methods=['GET'])
@jwt_required()
def get_order_history():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Parse pagination parameters
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        return jsonify({'error': 'page and per_page must be integers'}), 400

    query = Order.query.filter_by(user_id=user_id).order_by(desc(Order.created_at))

    result = paginate_query(query, page, per_page)

    return jsonify({
        'orders': [order.to_dict() for order in result['items']],
        'pagination': result['pagination']
    }), 200