from flask import Blueprint, request, jsonify, current_app  # ADDED current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, mail
from app.models.user import User
from app.utils.date_utils import format_datetime
import secrets
from flask_mail import Message

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'customer')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 409

    password_hash = generate_password_hash(password)
    verification_token = secrets.token_urlsafe(32)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,
        verification_token=verification_token
    )

    db.session.add(user)
    db.session.commit()

    # UPDATED: Skip email sending in test mode
    try:
        if not current_app.config.get('TESTING', False):
            msg = Message(
                subject='Verify your Book-A-Meal account',
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@bookmeal.com'),
                recipients=[email]
            )
            # Use FRONTEND_URL from config if available, fallback to localhost
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')
            msg.body = f'Click the link to verify your account: {frontend_url}/auth/verify/{verification_token}'
            mail.send(msg)
            print(f"Verification email sent to {email}")
        else:
            print(f"[TEST MODE] Would send verification email to {email}")
    except Exception as e:
        print(f"Email sending failed (non-blocking): {e}")

    return jsonify({
        'message': 'Registration successful! Check your email to verify your account.',
        'verification_token': verification_token  # Remove this in production
    }), 201


@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 400

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    return jsonify({'message': 'Email verified successfully! You can now log in.'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    if not user.is_verified:
        return jsonify({'error': 'Please verify your email before logging in'}), 403

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'member_since': format_datetime(user.created_at)
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'member_since': format_datetime(user.created_at)
    }), 200