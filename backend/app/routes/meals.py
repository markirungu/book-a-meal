from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.meals import Meal
from app.services.recipe_service import search_public_recipes
from app.utils.validators import parse_int

meals_bp = Blueprint('meals', __name__)


def validate_meal_data(data, is_update=False):
    """Validate meal data and return (is_valid, error_message)"""
    errors = []

    if not is_update:
        if 'name' not in data:
            errors.append('name is required')
        if 'price' not in data:
            errors.append('price is required')

    if 'name' in data:
        name = data['name'].strip()
        if not name:
            errors.append('name cannot be empty')
        elif len(name) > 100:
            errors.append('name cannot exceed 100 characters')

    if 'price' in data:
        try:
            price = float(data['price'])
            if price <= 0:
                errors.append('price must be greater than 0')
            if price > 10000:
                errors.append('price cannot exceed 10000')
        except (ValueError, TypeError):
            errors.append('price must be a valid number')

    if 'description' in data:
        description = data['description']
        if description and len(description) > 255:
            errors.append('description cannot exceed 255 characters')

    if 'image_url' in data:
        image_url = data['image_url']
        if image_url and len(image_url) > 255:
            errors.append('image_url cannot exceed 255 characters')

    return len(errors) == 0, errors


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
    
    # Use the more robust validation from person3
    is_valid, errors = validate_meal_data(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    name = data.get('name').strip()
    price = float(data.get('price'))

    # Check for duplicate names
    if Meal.query.filter_by(name=name).first():
        return jsonify({'error': 'A meal with this name already exists'}), 409

    meal = Meal(
        caterer_id=user.caterer_id,
        name=name,
        description=data.get('description'),
        price=price,
        image_url=data.get('image_url'),
        ingredients=data.get('ingredients', []),        # KEPT from develop
        recipe_source=data.get('recipe_source')         # KEPT from develop
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
    
    # Use person3's more robust validation
    is_valid, errors = validate_meal_data(data, is_update=True)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400

    # Check for duplicate names (excluding current meal)
    if 'name' in data:
        new_name = data['name'].strip()
        existing_meal = Meal.query.filter_by(name=new_name).first()
        if existing_meal and existing_meal.id != meal_id:
            return jsonify({'error': 'A meal with this name already exists'}), 409
        meal.name = new_name

    if 'description' in data:
        meal.description = data['description']
    if 'price' in data:
        meal.price = float(data['price'])
    if 'image_url' in data:
        meal.image_url = data['image_url']
    if 'ingredients' in data:                          # KEPT from develop
        meal.ingredients = data.get('ingredients') or []
    if 'recipe_source' in data:                        # KEPT from develop
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