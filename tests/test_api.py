import pytest
from datetime import date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.meal import Meal, Menu
from app.models.order import Order


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username='admin', email='admin@test.com', role='admin')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def customer_user(app):
    with app.app_context():
        user = User(username='customer', email='customer@test.com', role='customer')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_meals(app):
    with app.app_context():
        meals = [
            Meal(name='Pizza', description='Delicious pizza', price=15.99),
            Meal(name='Burger', description='Juicy burger', price=12.50),
            Meal(name='Salad', description='Fresh salad', price=8.99)
        ]
        for meal in meals:
            db.session.add(meal)
        db.session.commit()
        return meals


@pytest.fixture
def auth_headers(client, admin_user):
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'password'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def customer_auth_headers(client, customer_user):
    response = client.post('/auth/login', json={
        'username': 'customer',
        'password': 'password'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


class TestMenuEndpoints:
    def test_create_menu_success(self, client, auth_headers, sample_meals):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        response = client.post('/menus', json={
            'date': tomorrow,
            'meal_ids': [sample_meals[0].id, sample_meals[1].id]
        }, headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'menu' in data
        assert data['menu']['date'] == tomorrow
        assert len(data['menu']['meals']) == 2

    def test_create_menu_validation_errors(self, client, auth_headers):
        # Missing date
        response = client.post('/menus', json={
            'meal_ids': [1, 2]
        }, headers=auth_headers)
        assert response.status_code == 400

        # Empty meal_ids
        response = client.post('/menus', json={
            'date': date.today().isoformat(),
            'meal_ids': []
        }, headers=auth_headers)
        assert response.status_code == 400

        # Invalid date format
        response = client.post('/menus', json={
            'date': 'invalid-date',
            'meal_ids': [1]
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_create_menu_duplicate_date(self, client, auth_headers, sample_meals):
        menu_date = date.today().isoformat()
        # Create first menu
        client.post('/menus', json={
            'date': menu_date,
            'meal_ids': [sample_meals[0].id]
        }, headers=auth_headers)

        # Try to create duplicate
        response = client.post('/menus', json={
            'date': menu_date,
            'meal_ids': [sample_meals[1].id]
        }, headers=auth_headers)
        assert response.status_code == 409

    def test_get_menus_pagination(self, client, auth_headers, sample_meals):
        # Create multiple menus
        for i in range(5):
            menu_date = (date.today() + timedelta(days=i)).isoformat()
            client.post('/menus', json={
                'date': menu_date,
                'meal_ids': [sample_meals[0].id]
            }, headers=auth_headers)

        # Test pagination
        response = client.get('/menus?page=1&per_page=2', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'menus' in data
        assert 'pagination' in data
        assert len(data['menus']) == 2
        assert data['pagination']['total'] == 5
        assert data['pagination']['total_pages'] == 3

    def test_get_menu_by_id(self, client, auth_headers, sample_meals):
        # Create menu
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        create_response = client.post('/menus', json={
            'date': tomorrow,
            'meal_ids': [sample_meals[0].id]
        }, headers=auth_headers)
        menu_id = create_response.get_json()['menu']['id']

        # Get menu by ID
        response = client.get(f'/menus/{menu_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == menu_id
        assert data['date'] == tomorrow

    def test_update_menu(self, client, auth_headers, sample_meals):
        # Create menu
        menu_date = date.today().isoformat()
        create_response = client.post('/menus', json={
            'date': menu_date,
            'meal_ids': [sample_meals[0].id]
        }, headers=auth_headers)
        menu_id = create_response.get_json()['menu']['id']

        # Update menu
        new_date = (date.today() + timedelta(days=1)).isoformat()
        response = client.put(f'/menus/{menu_id}', json={
            'date': new_date,
            'meal_ids': [sample_meals[1].id, sample_meals[2].id]
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['menu']['date'] == new_date
        assert len(data['menu']['meals']) == 2

    def test_delete_menu(self, client, auth_headers, sample_meals):
        # Create menu
        menu_date = date.today().isoformat()
        create_response = client.post('/menus', json={
            'date': menu_date,
            'meal_ids': [sample_meals[0].id]
        }, headers=auth_headers)
        menu_id = create_response.get_json()['menu']['id']

        # Delete menu
        response = client.delete(f'/menus/{menu_id}', headers=auth_headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f'/menus/{menu_id}', headers=auth_headers)
        assert response.status_code == 404


class TestOrderEndpoints:
    def test_create_order_success(self, client, customer_auth_headers, sample_meals):
        # Create today's menu first
        admin_response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        admin_token = admin_response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        today = date.today().isoformat()
        client.post('/menus', json={
            'date': today,
            'meal_ids': [sample_meals[0].id, sample_meals[1].id]
        }, headers=admin_headers)

        # Place order
        response = client.post('/orders', json={
            'meal_id': sample_meals[0].id,
            'quantity': 2
        }, headers=customer_auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'order' in data
        assert data['order']['meal_id'] == sample_meals[0].id
        assert data['order']['quantity'] == 2
        assert data['order']['status'] == 'pending'

    def test_create_order_validation_errors(self, client, customer_auth_headers):
        # Missing meal_id
        response = client.post('/orders', json={
            'quantity': 1
        }, headers=customer_auth_headers)
        assert response.status_code == 400

        # Invalid quantity
        response = client.post('/orders', json={
            'meal_id': 1,
            'quantity': 0
        }, headers=customer_auth_headers)
        assert response.status_code == 400

    def test_create_order_meal_not_in_menu(self, client, customer_auth_headers, sample_meals):
        # Try to order a meal not in today's menu
        response = client.post('/orders', json={
            'meal_id': sample_meals[0].id,
            'quantity': 1
        }, headers=customer_auth_headers)
        assert response.status_code == 400

    def test_get_orders_pagination(self, client, customer_auth_headers, sample_meals):
        # Create today's menu
        admin_response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        admin_token = admin_response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        today = date.today().isoformat()
        client.post('/menus', json={
            'date': today,
            'meal_ids': [sample_meals[0].id, sample_meals[1].id]
        }, headers=admin_headers)

        # Create multiple orders
        for _ in range(5):
            client.post('/orders', json={
                'meal_id': sample_meals[0].id,
                'quantity': 1
            }, headers=customer_auth_headers)

        # Test pagination
        response = client.get('/orders?page=1&per_page=2', headers=customer_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
        assert 'pagination' in data
        assert len(data['orders']) == 2

    def test_update_order(self, client, customer_auth_headers, sample_meals):
        # Create today's menu with both meals
        admin_response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        admin_token = admin_response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        today = date.today().isoformat()
        client.post('/menus', json={
            'date': today,
            'meal_ids': [sample_meals[0].id, sample_meals[1].id]
        }, headers=admin_headers)

        # Create order
        create_response = client.post('/orders', json={
            'meal_id': sample_meals[0].id,
            'quantity': 1
        }, headers=customer_auth_headers)
        order_id = create_response.get_json()['order']['id']

        # Update order
        response = client.put(f'/orders/{order_id}', json={
            'meal_id': sample_meals[1].id,
            'quantity': 3
        }, headers=customer_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['order']['meal_id'] == sample_meals[1].id
        assert data['order']['quantity'] == 3

    def test_delete_order(self, client, customer_auth_headers, sample_meals):
        # Create today's menu
        admin_response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        admin_token = admin_response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        today = date.today().isoformat()
        client.post('/menus', json={
            'date': today,
            'meal_ids': [sample_meals[0].id]
        }, headers=admin_headers)

        # Create order
        create_response = client.post('/orders', json={
            'meal_id': sample_meals[0].id,
            'quantity': 1
        }, headers=customer_auth_headers)
        order_id = create_response.get_json()['order']['id']

        # Delete order
        response = client.delete(f'/orders/{order_id}', headers=customer_auth_headers)
        assert response.status_code == 200

    def test_get_order_history(self, client, customer_auth_headers, sample_meals):
        # Create today's menu
        admin_response = client.post('/auth/login', json={
            'username': 'admin',
            'password': 'password'
        })
        admin_token = admin_response.get_json()['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}

        today = date.today().isoformat()
        client.post('/menus', json={
            'date': today,
            'meal_ids': [sample_meals[0].id]
        }, headers=admin_headers)

        # Create order
        client.post('/orders', json={
            'meal_id': sample_meals[0].id,
            'quantity': 1
        }, headers=customer_auth_headers)

        # Get history
        response = client.get('/orders/history', headers=customer_auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
        assert len(data['orders']) >= 1