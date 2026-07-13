import pytest

class TestRateLimit:

    def test_login_rate_limiting(self, client):
        client.application.config['RATELIMIT_ENABLED'] = True
        try:
            # Make 10 requests; should fail with 400 (missing fields) or 401 (unauthorized) but NOT 429
            for i in range(10):
                res = client.post('/api/auth/login', json={
                    'username': f'nonexistent_user_{i}'
                })
                assert res.status_code == 400 or res.status_code == 401

            # The 11th request should be rate limited
            res = client.post('/api/auth/login', json={
                'username': 'nonexistent_user_11'
            })
            assert res.status_code == 429
            assert 'too many requests' in res.get_json()['error'].lower()
        finally:
            client.application.config['RATELIMIT_ENABLED'] = False

    def test_signup_rate_limiting(self, client):
        client.application.config['RATELIMIT_ENABLED'] = True
        try:
            # Make 10 valid signup requests; should succeed with 201
            for i in range(10):
                res = client.post('/api/auth/signup', json={
                    'username': f'rate_signup_user_{i}',
                    'first_name': 'Rate',
                    'email': f'rate_signup_{i}@example.com',
                    'password': 'password123'
                })
                assert res.status_code == 201

            # The 11th signup request should be rate limited
            res = client.post('/api/auth/signup', json={
                'username': 'rate_signup_user_11',
                'first_name': 'Rate',
                'email': 'rate_signup_11@example.com',
                'password': 'password123'
            })
            assert res.status_code == 429
            assert 'too many requests' in res.get_json()['error'].lower()
        finally:
            client.application.config['RATELIMIT_ENABLED'] = False
