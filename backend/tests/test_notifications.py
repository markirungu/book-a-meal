import pytest
import json
from app import create_app, db
from app.models.user import User
from app.models.notification import Notification


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    test_config = {
        'TESTING': True,
        'MAIL_SUPPRESS_SEND': True,
        'JWT_SECRET_KEY': 'test-secret-key',
        'SECRET_KEY': 'test-secret-key',
    }
    
    app = create_app(test_config=test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def customer_token(client):
    """Create a verified customer and return JWT token."""
    client.post('/auth/register', json={
        'name': 'Test Customer',
        'email': 'customer@test.com',
        'password': 'password123',
        'role': 'customer'
    })
    # Get verification token (simplified for test)
    from app.models.user import User
    user = User.query.filter_by(email='customer@test.com').first()
    user.is_verified = True
    db.session.commit()
    
    login = client.post('/auth/login', json={
        'email': 'customer@test.com',
        'password': 'password123'
    })
    return json.loads(login.data)['access_token']


@pytest.fixture
def admin_token(client):
    """Create an admin and return JWT token."""
    client.post('/auth/register', json={
        'name': 'Test Admin',
        'email': 'admin@test.com',
        'password': 'password123',
        'role': 'admin'
    })
    from app.models.user import User
    user = User.query.filter_by(email='admin@test.com').first()
    user.is_verified = True
    db.session.commit()
    
    login = client.post('/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password123'
    })
    return json.loads(login.data)['access_token']


def test_get_notifications_empty(client, customer_token):
    """GET /notifications returns empty list for new user."""
    response = client.get('/notifications',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data'] == []
    assert data['meta']['total'] == 0
    assert data['meta']['unread_count'] == 0


def test_get_notifications_with_pagination(client, customer_token, admin_token):
    """GET /notifications respects pagination."""
    # Admin creates notifications for customer
    from app.models.user import User
    customer = User.query.filter_by(email='customer@test.com').first()
    
    for i in range(15):
        client.post('/notifications',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'user_id': customer.id,
                'title': f'Test {i}',
                'message': f'Message {i}'
            })
    
    response = client.get('/notifications?page=2&per_page=5',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['meta']['page'] == 2
    assert data['meta']['per_page'] == 5
    assert len(data['data']) == 5


def test_mark_notification_as_read(client, customer_token, admin_token):
    """PATCH /notifications/<id>/read marks notification as read."""
    from app.models.user import User
    customer = User.query.filter_by(email='customer@test.com').first()
    
    # Create notification
    create_resp = client.post('/notifications',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'user_id': customer.id,
            'title': 'Test Notification',
            'message': 'This is a test'
        })
    assert create_resp.status_code == 201
    
    # Get notifications
    get_resp = client.get('/notifications',
        headers={'Authorization': f'Bearer {customer_token}'})
    notification_id = json.loads(get_resp.data)['data'][0]['id']
    
    # Mark as read
    patch_resp = client.patch(f'/notifications/{notification_id}/read',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert patch_resp.status_code == 200
    assert json.loads(patch_resp.data)['notification']['is_read'] is True


def test_mark_all_as_read(client, customer_token, admin_token):
    """PATCH /notifications/read-all marks all as read."""
    from app.models.user import User
    customer = User.query.filter_by(email='customer@test.com').first()
    
    # Create multiple notifications
    for i in range(3):
        client.post('/notifications',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'user_id': customer.id,
                'title': f'Test {i}',
                'message': f'Message {i}'
            })
    
    # Mark all as read
    response = client.patch('/notifications/read-all',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert response.status_code == 200
    
    # Verify all read
    get_resp = client.get('/notifications?show_all=true',
        headers={'Authorization': f'Bearer {customer_token}'})
    data = json.loads(get_resp.data)
    assert all(n['is_read'] for n in data['data'])


def test_create_notification_as_customer_fails(client, customer_token):
    """Customer cannot create notifications."""
    response = client.post('/notifications',
        headers={'Authorization': f'Bearer {customer_token}'},
        json={
            'title': 'Unauthorized',
            'message': 'Should fail'
        })
    assert response.status_code == 403


def test_create_notification_missing_fields(client, admin_token):
    """Creating notification without title/message fails."""
    response = client.post('/notifications',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'title': 'Missing message'})
    assert response.status_code == 400


def test_get_notifications_without_token(client):
    """Unauthenticated request returns 401."""
    response = client.get('/notifications')
    assert response.status_code == 401


def test_get_unread_count(client, customer_token, admin_token):
    """GET /notifications/unread-count returns correct count."""
    from app.models.user import User
    customer = User.query.filter_by(email='customer@test.com').first()
    
    # Create 3 notifications
    for i in range(3):
        client.post('/notifications',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'user_id': customer.id,
                'title': f'Test {i}',
                'message': f'Message {i}'
            })
    
    response = client.get('/notifications/unread-count',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert response.status_code == 200
    assert json.loads(response.data)['unread_count'] == 3


def test_notification_not_found(client, customer_token):
    """PATCH non-existent notification returns 404."""
    response = client.patch('/notifications/99999/read',
        headers={'Authorization': f'Bearer {customer_token}'})
    assert response.status_code == 404