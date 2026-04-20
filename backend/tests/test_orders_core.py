import json
from datetime import datetime, timedelta

from app import db
from app.models.caterer import Caterer
from app.models.meals import Meal, Menu, MenuItem
from app.models.user import User


def _create_and_verify(client, name, email, password, role='customer'):
    client.post('/auth/register', json={
        'name': name,
        'email': email,
        'password': password,
        'role': role,
    })
    user = User.query.filter_by(email=email).first()
    user.is_verified = True
    db.session.commit()
    return user


def _login(client, email, password):
    response = client.post('/auth/login', json={'email': email, 'password': password})
    return json.loads(response.data)['access_token']


def test_customer_place_order_and_history(client):
    admin = _create_and_verify(client, 'Admin', 'admin_orders@test.com', 'pass123', role='admin')
    customer = _create_and_verify(client, 'Customer', 'customer_orders@test.com', 'pass123', role='customer')

    caterer = Caterer(name='Main Kitchen', owner_user_id=admin.id)
    db.session.add(caterer)
    db.session.flush()
    admin.caterer_id = caterer.id

    meal = Meal(name='Chicken Pilau', description='Tasty', price=700, caterer_id=caterer.id)
    db.session.add(meal)
    db.session.flush()

    menu = Menu(
        caterer_id=caterer.id,
        date=datetime.utcnow().date(),
        created_by=admin.id,
        cutoff_time=datetime.utcnow() + timedelta(hours=2),
        is_published=True,
    )
    db.session.add(menu)
    db.session.flush()
    db.session.add(MenuItem(menu_id=menu.id, meal_id=meal.id, is_special=True))
    db.session.commit()

    customer_token = _login(client, 'customer_orders@test.com', 'pass123')
    response = client.post('/orders', json={
        'menu_id': menu.id,
        'meal_id': meal.id,
        'quantity': 2,
    }, headers={'Authorization': f'Bearer {customer_token}'})

    assert response.status_code == 201
    order = json.loads(response.data)['order']
    assert order['status'] == 'pending'
    assert order['total_price'] == 1400

    history = client.get('/orders/history', headers={'Authorization': f'Bearer {customer_token}'})
    assert history.status_code == 200
    assert len(json.loads(history.data)['data']) >= 1


def test_admin_revenue_and_analytics(client):
    admin = _create_and_verify(client, 'Admin 2', 'admin_analytics@test.com', 'pass123', role='admin')

    caterer = Caterer(name='Analytics Kitchen', owner_user_id=admin.id)
    db.session.add(caterer)
    db.session.flush()
    admin.caterer_id = caterer.id

    meal = Meal(name='Beef and Rice', description='Classic', price=500, caterer_id=caterer.id)
    db.session.add(meal)
    db.session.flush()

    menu = Menu(
        caterer_id=caterer.id,
        date=datetime.utcnow().date(),
        created_by=admin.id,
        is_published=True,
    )
    db.session.add(menu)
    db.session.flush()
    db.session.add(MenuItem(menu_id=menu.id, meal_id=meal.id))

    from app.models.order import Order
    order = Order(
        customer_id=admin.id,
        caterer_id=caterer.id,
        menu_id=menu.id,
        meal_id=meal.id,
        quantity=3,
        unit_price=500,
        status='completed',
    )
    db.session.add(order)
    db.session.commit()

    admin_token = _login(client, 'admin_analytics@test.com', 'pass123')
    revenue = client.get('/orders/admin/revenue?fulfilled_only=true', headers={'Authorization': f'Bearer {admin_token}'})
    assert revenue.status_code == 200
    assert json.loads(revenue.data)['data']['total_revenue'] == 1500

    analytics = client.get('/orders/admin/analytics', headers={'Authorization': f'Bearer {admin_token}'})
    assert analytics.status_code == 200
    payload = json.loads(analytics.data)['data']
    assert 'top_meals' in payload
    assert 'peak_days' in payload
