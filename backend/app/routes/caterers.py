from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.caterer import Caterer
from app.models.user import User

caterers_bp = Blueprint('caterers', __name__)


@caterers_bp.route('', methods=['POST'])
@jwt_required()
def create_caterer():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    payload = request.get_json() or {}
    name = (payload.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400

    caterer = Caterer(
        name=name,
        description=payload.get('description'),
        owner_user_id=user.id,
    )
    db.session.add(caterer)
    db.session.flush()

    user.caterer_id = caterer.id
    db.session.commit()
    return jsonify({'message': 'Caterer created', 'data': caterer.to_dict()}), 201


@caterers_bp.route('', methods=['GET'])
def list_caterers():
    data = [c.to_dict() for c in Caterer.query.order_by(Caterer.created_at.desc()).all()]
    return jsonify({'data': data}), 200
