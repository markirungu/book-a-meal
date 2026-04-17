import pytest
import json
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['MAIL_SUPPRESS_SEND'] = True  # ADDED: Prevents actual email sending
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_success(client):
    response = client.post('/auth/register', 
        json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'verification_token' in data

def test_register_missing_fields(client):
    response = client.post('/auth/register',
        json={'email': 'test@example.com'})
    assert response.status_code == 400

def test_register_duplicate_email(client):
    client.post('/auth/register',
        json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    response = client.post('/auth/register',
        json={
            'name': 'Test User 2',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    assert response.status_code == 409

def test_login_unverified_user(client):
    client.post('/auth/register',
        json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    response = client.post('/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'password123'
        })
    assert response.status_code == 403

def test_login_verified_user(client):
    reg_response = client.post('/auth/register',
        json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    token = json.loads(reg_response.data)['verification_token']
    client.get(f'/auth/verify/{token}')
    
    response = client.post('/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'password123'
        })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_login_wrong_password(client):
    reg_response = client.post('/auth/register',
        json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'role': 'customer'
        })
    token = json.loads(reg_response.data)['verification_token']
    client.get(f'/auth/verify/{token}')
    
    response = client.post('/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
    assert response.status_code == 401

def test_verify_invalid_token(client):
    response = client.get('/auth/verify/invalidtoken123')
    assert response.status_code == 400

def test_protected_route_without_token(client):
    response = client.get('/auth/me')
    assert response.status_code == 401