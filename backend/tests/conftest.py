import sys
import os
import pytest

# ensure 'backend/' is on the path so imports like 'from models.base import db' resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models.base import db
from routes.auth_routes import auth_bp


@pytest.fixture
def app():
    test_app = Flask(__name__)
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['TESTING'] = True

    db.init_app(test_app)
    test_app.register_blueprint(auth_bp)

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """Creates a user in the DB and returns their credentials for login tests."""
    payload = {'username': 'testuser', 'email': 'test@example.com', 'password': 'secret123'}
    client.post('/api/auth/signup', json=payload)
    return payload
