import pytest
import json
from app import create_app, db
from app.models.user import User

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
    """Test client for making requests."""
    return app.test_client()
