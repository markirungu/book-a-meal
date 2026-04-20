from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.meals import Meal
from app.services.recipe_service import search_public_recipes
from app.utils.validators import parse_int

meals_bp = Blueprint('meals', __name__)


# ── helper: guard admin-only endpoints ──────────────────────────────────────
def admin_required():
    """Returns (user, error_response). Call at the top of every admin route."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


def validate_meal_payload(data, partial=False):
    errors = []
    if not partial and not data.get('name'):
        errors.append('name is required')
    if not partial and data.get('price') is None:
        errors.append('price is required')

    if data.get('name') and len(data.get('name')) > 100:
        errors.append('name must be <= 100 characters')
    if data.get('description') and len(data.get('description')) > 255:
        errors.append('description must be <= 255 characters')

    if data.get('price') is not None:
        try:
            if float(data.get('price')) <= 0:
                errors.append('price must be greater than 0')
        except (TypeError, ValueError):
            errors.append('price must be numeric')

    return errors


# ── POST /meals  — create a meal option ─────────────────────────────────────
@meals_bp.route('', methods=['POST'])
@jwt_required()
def create_meal():
    user, err = admin_required()
    if err:
        return err

    data = request.get_json()
    errors = validate_meal_payload(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    existing = Meal.query.filter_by(name=data.get('name')).first()
    if existing:
        return jsonify({'error': 'Meal with this name already exists'}), 409

    meal = Meal(
        caterer_id=user.caterer_id,
        name=data.get('name').strip(),
        description=data.get('description'),
        price=float(data.get('price')),
        image_url=data.get('image_url'),
        ingredients=data.get('ingredients', []),
        recipe_source=data.get('recipe_source')
    )
    db.session.add(meal)
    db.session.commit()

    return jsonify({'message': 'Meal created', 'meal': meal.to_dict()}), 201


# ── GET /meals  — list all meal options (any authenticated user) ─────────────
@meals_bp.route('', methods=['GET'])
@jwt_required()
def get_meals():
    caterer_id = parse_int(request.args.get('caterer_id'))
    query = Meal.query
    if caterer_id:
        query = query.filter_by(caterer_id=caterer_id)
    meals = query.order_by(Meal.name).all()
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
    if meal.caterer_id and user.caterer_id and meal.caterer_id != user.caterer_id:
        return jsonify({'error': 'Cannot modify another caterer\'s meal'}), 403

    data = request.get_json()
    errors = validate_meal_payload(data, partial=True)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    meal.name = data.get('name', meal.name).strip() if data.get('name') else meal.name
    meal.description = data.get('description', meal.description)
    meal.price = float(data.get('price', meal.price))
    meal.image_url = data.get('image_url', meal.image_url)
    if 'ingredients' in data:
        meal.ingredients = data.get('ingredients') or []
    if 'recipe_source' in data:
        meal.recipe_source = data.get('recipe_source')

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
    if meal.caterer_id and user.caterer_id and meal.caterer_id != user.caterer_id:
        return jsonify({'error': 'Cannot delete another caterer\'s meal'}), 403

    db.session.delete(meal)
    db.session.commit()
    return jsonify({'message': 'Meal deleted'}), 200


@meals_bp.route('/recipes/search', methods=['GET'])
@jwt_required()
def search_recipes():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'q is required'}), 400
    try:
        return jsonify({'results': search_public_recipes(query)}), 200
    except Exception as exc:
        return jsonify({'error': f'Recipe API failed: {str(exc)}'}), 502