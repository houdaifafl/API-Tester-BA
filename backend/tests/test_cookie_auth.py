class TestCookieAuth:

    def test_login_sets_cookie(self, client):
        # 1. Signup a user
        client.post('/api/auth/signup', json={
            'username': 'cookieuser',
            'first_name': 'Cookie',
            'email': 'cookie@example.com',
            'password': 'pass123'
        })
        
        # 2. Perform login and check Set-Cookie header
        res = client.post('/api/auth/login', json={
            'username': 'cookieuser',
            'password': 'pass123'
        })
        assert res.status_code == 200
        assert 'Set-Cookie' in res.headers
        cookie_header = res.headers['Set-Cookie']
        assert 'token=' in cookie_header
        assert 'HttpOnly' in cookie_header
        assert 'SameSite=Lax' in cookie_header

    def test_logout_clears_cookie(self, client):
        # 1. Signup and login
        client.post('/api/auth/signup', json={
            'username': 'logoutuser',
            'first_name': 'Logout',
            'email': 'logout@example.com',
            'password': 'pass123'
        })
        client.post('/api/auth/login', json={
            'username': 'logoutuser',
            'password': 'pass123'
        })

        # 2. Perform logout and check Set-Cookie header to clear token
        res = client.post('/api/auth/logout')
        assert res.status_code == 200
        assert 'Set-Cookie' in res.headers
        cookie_header = res.headers['Set-Cookie']
        assert 'token=;' in cookie_header or 'token=""' in cookie_header or 'Expires=' in cookie_header

    def test_protected_route_with_cookie(self, client):
        # 1. Signup and login to get the cookie set in client session
        client.post('/api/auth/signup', json={
            'username': 'routeuser',
            'first_name': 'Route',
            'email': 'route@example.com',
            'password': 'pass123'
        })
        client.post('/api/auth/login', json={
            'username': 'routeuser',
            'password': 'pass123'
        })

        # 2. Make authenticated request (Flask test client automatically stores/sends cookies)
        res = client.get('/api/workspaces')
        assert res.status_code == 200

    def test_protected_route_fails_without_cookie(self, client):
        # Make a request without any cookie
        res = client.get('/api/workspaces')
        assert res.status_code == 401
        assert 'Unauthorized' in res.get_json()['error']
