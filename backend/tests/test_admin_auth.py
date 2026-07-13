import pytest
from models.base import db
from models.user_model import User

class TestAdminAuth:

    def test_get_me_unauthenticated(self, client):
        client._cookies.clear()
        res = client.get('/api/auth/me')
        assert res.status_code == 401

    def test_get_me_authenticated_user(self, client):
        client._cookies.clear()
        # Signup and login a normal user
        client.post('/api/auth/signup', json={
            'username': 'user1',
            'first_name': 'User',
            'email': 'user1@example.com',
            'password': 'password123'
        })
        login_res = client.post('/api/auth/login', json={
            'username': 'user1',
            'password': 'password123'
        })
        assert login_res.status_code == 200

        me_res = client.get('/api/auth/me')
        assert me_res.status_code == 200
        data = me_res.get_json()
        assert data['username'] == 'user1'
        assert data['is_admin'] is False

    def test_get_me_authenticated_admin(self, client, app):
        client._cookies.clear()
        # Signup an admin user
        client.post('/api/auth/signup', json={
            'username': 'admin1',
            'first_name': 'Admin',
            'email': 'admin1@example.com',
            'password': 'password123'
        })
        # Promote user to admin in DB
        with app.app_context():
            user = User.query.filter_by(username='admin1').first()
            user.is_admin = True
            db.session.commit()

        login_res = client.post('/api/auth/login', json={
            'username': 'admin1',
            'password': 'password123'
        })
        assert login_res.status_code == 200

        me_res = client.get('/api/auth/me')
        assert me_res.status_code == 200
        data = me_res.get_json()
        assert data['username'] == 'admin1'
        assert data['is_admin'] is True

    def test_admin_required_decorator_rejects_user(self, client):
        client._cookies.clear()
        # Login normal user
        client.post('/api/auth/signup', json={
            'username': 'user2',
            'first_name': 'User',
            'email': 'user2@example.com',
            'password': 'password123'
        })
        client.post('/api/auth/login', json={
            'username': 'user2',
            'password': 'password123'
        })

        # Try to hit admin endpoint
        res = client.get('/api/admin/users')
        assert res.status_code == 403
        assert 'forbidden' in res.get_json()['error'].lower() or 'admin privilege' in res.get_json()['error'].lower()

    def test_admin_required_decorator_allows_admin(self, client, app):
        client._cookies.clear()
        # Signup admin
        client.post('/api/auth/signup', json={
            'username': 'admin2',
            'first_name': 'Admin',
            'email': 'admin2@example.com',
            'password': 'password123'
        })
        with app.app_context():
            user = User.query.filter_by(username='admin2').first()
            user.is_admin = True
            db.session.commit()

        client.post('/api/auth/login', json={
            'username': 'admin2',
            'password': 'password123'
        })

        # Hit admin endpoint
        res = client.get('/api/admin/users')
        assert res.status_code == 200
