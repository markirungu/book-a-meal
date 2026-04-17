from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.meals import Meal

meals_bp = Blueprint('meals', __name__)


# ── helper: guard admin-only endpoints ──────────────────────────────────────
def admin_required():
    """Returns (user, error_response). Call at the top of every admin route."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


# ── POST /meals  — create a meal option ─────────────────────────────────────
@meals_bp.route('', methods=['POST'])
@jwt_required()
def create_meal():
    user, err = admin_required()
    if err:
        return err

    data = request.get_json()
    name = data.get('name')
    price = data.get('price')

    if not name or price is None:
        return jsonify({'error': 'name and price are required'}), 400

    meal = Meal(
        name=name,
        description=data.get('description'),
        price=float(price),
        image_url=data.get('image_url')
    )
    db.session.add(meal)
    db.session.commit()

    return jsonify({'message': 'Meal created', 'meal': meal.to_dict()}), 201


# ── GET /meals  — list all meal options (any authenticated user) ─────────────
@meals_bp.route('', methods=['GET'])
@jwt_required()
def get_meals():
    meals = Meal.query.order_by(Meal.name).all()
    return jsonify([m.to_dict() for m in meals]), 200


# ── GET /meals/<id>  — single meal ──────────────────────────────────────────
@meals_bp.route('/<int:meal_id>', methods=['GET'])
@jwt_required()
def get_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    return jsonify(meal.to_dict()), 200


# ── PUT /meals/<id>  — update a meal (admin only) ───────────────────────────
@meals_bp.route('/<int:meal_id>', methods=['PUT'])
@jwt_required()
def update_meal(meal_id):
    user, err = admin_required()
    if err:
        return err

    meal = Meal.query.get_or_404(meal_id)
    data = request.get_json()

    meal.name = data.get('name', meal.name)
    meal.description = data.get('description', meal.description)
    meal.price = float(data.get('price', meal.price))
    meal.image_url = data.get('image_url', meal.image_url)

    db.session.commit()
    return jsonify({'message': 'Meal updated', 'meal': meal.to_dict()}), 200


# ── DELETE /meals/<id>  — delete a meal (admin only) ────────────────────────
@meals_bp.route('/<int:meal_id>', methods=['DELETE'])
@jwt_required()
def delete_meal(meal_id):
    user, err = admin_required()
    if err:
        return err

    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({'message': 'Meal deleted'}), 200