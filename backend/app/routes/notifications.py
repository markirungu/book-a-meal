from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.notification import Notification
from app.models.user import User
from app.utils.date_utils import format_datetime

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get current user's notifications with pagination."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Only show unread by default, or all if specified
    show_all = request.args.get('show_all', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=user_id)
    if not show_all:
        query = query.filter_by(is_read=False)
    
    paginated = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'data': [n.to_dict() for n in paginated.items],
        'meta': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count()
        }
    }), 200


@notifications_bp.route('/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark a notification as read."""
    user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id, user_id=user_id
    ).first()
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200


@notifications_bp.route('/read-all', methods=['PATCH'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read for current user."""
    user_id = get_jwt_identity()
    
    result = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({
        'message': f'{result} notifications marked as read'
    }), 200


@notifications_bp.route('', methods=['POST'])
@jwt_required()
def create_notification():
    """Admin only: Create a notification for user(s)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    target_user_id = data.get('user_id')
    title = data.get('title')
    message = data.get('message')
    notification_type = data.get('notification_type', 'general')
    
    if not title or not message:
        return jsonify({'error': 'Title and message are required'}), 400
    
    # If no specific user, send to all customers
    if target_user_id:
        user = User.query.get(target_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        notification = Notification(
            user_id=target_user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Notification sent',
            'notification': notification.to_dict()
        }), 201
    
    else:
        # Send to all customers
        customers = User.query.filter_by(role='customer').all()
        notifications = []
        for customer in customers:
            notification = Notification(
                user_id=customer.id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Notification sent to {len(customers)} customers',
            'count': len(customers)
        }), 201


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications for current user."""
    user_id = get_jwt_identity()
    
    count = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).count()
    
    return jsonify({'unread_count': count}), 200