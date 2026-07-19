import sys
import os
import pytest

# ensure 'backend/' is on the path so imports like 'from models.base import db' resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models.base import db
from extensions import limiter
from routes.auth_routes import auth_bp
from routes.workspace_routes import workspace_bp
from routes.collection_routes import collection_bp
from routes.request_routes import request_bp
from routes.api_client_routes import api_client_bp
from routes.history_routes import history_bp
from routes.invitation_routes import invitation_bp
from routes.admin_routes import admin_bp
from routes.comment_routes import comment_bp
from routes.analytics_routes import analytics_bp
from routes.activity_routes import activity_bp


@pytest.fixture
def app():
    test_app = Flask(__name__)
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    test_app.config['TESTING'] = True

    db.init_app(test_app)
    limiter.init_app(test_app)

    from app import register_security_headers
    register_security_headers(test_app)

    from flask import jsonify
    from flask_limiter.errors import RateLimitExceeded
    @test_app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(e):
        return jsonify({'error': 'Too Many Requests', 'message': str(e.description)}), 429
    test_app.register_blueprint(auth_bp)
    test_app.register_blueprint(workspace_bp)
    test_app.register_blueprint(collection_bp)
    test_app.register_blueprint(request_bp)
    test_app.register_blueprint(api_client_bp)
    test_app.register_blueprint(history_bp)
    test_app.register_blueprint(invitation_bp)
    test_app.register_blueprint(admin_bp)
    test_app.register_blueprint(comment_bp)
    test_app.register_blueprint(analytics_bp)
    test_app.register_blueprint(activity_bp)


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
    payload = {'username': 'testuser', 'first_name': 'Test', 'email': 'test@example.com', 'password': 'secret123'}
    client.post('/api/auth/signup', json=payload)
    return payload


@pytest.fixture
def auth_data(client):
    """Signs up + logs in a test user. Returns login response payload with user_id and default_workspace_id."""
    client.post('/api/auth/signup', json={
        'username': 'testuser',
        'first_name': 'Test',
        'email': 'test@example.com',
        'password': 'secret123'
    })
    res = client.post('/api/auth/login', json={'username': 'testuser', 'password': 'secret123'})
    return res.get_json()


def signup_and_login(client, username, email):
    """Helper to create a second user and return their auth data."""
    client.post('/api/auth/signup', json={
        'username': username,
        'first_name': username.capitalize(),
        'email': email,
        'password': 'pass123'
    })
    res = client.post('/api/auth/login', json={'username': username, 'password': 'pass123'})
    return res.get_json()


@pytest.fixture
def auth_client(client, auth_data):
    token = auth_data['token']
    class AuthenticatedClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token
            self.headers = {'Authorization': f'Bearer {token}'}

        def _add_headers(self, kwargs):
            headers = kwargs.get('headers', {})
            if isinstance(headers, list):
                headers = dict(headers)
            else:
                headers = dict(headers)
            headers.update(self.headers)
            kwargs['headers'] = headers

        def get(self, *args, **kwargs):
            self._add_headers(kwargs)
            return self.client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            self._add_headers(kwargs)
            return self.client.post(*args, **kwargs)

        def patch(self, *args, **kwargs):
            self._add_headers(kwargs)
            return self.client.patch(*args, **kwargs)

        def delete(self, *args, **kwargs):
            self._add_headers(kwargs)
            return self.client.delete(*args, **kwargs)

    return AuthenticatedClient(client, token)


@pytest.fixture(autouse=True)
def clear_cookies(client):
    """Automatically clear client cookies before every test to ensure isolation."""
    client._cookies.clear()
