class TestSignup:

    def test_valid_signup(self, client):
        res = client.post('/api/auth/signup', json={
            'username': 'alice',
            'first_name': 'Alice',
            'email': 'alice@example.com',
            'password': 'pass123'
        })
        assert res.status_code == 201
        assert res.get_json()['message'] == 'User created successfully'

    def test_missing_username(self, client):
        res = client.post('/api/auth/signup', json={
            'first_name': 'Alice',
            'email': 'alice@example.com',
            'password': 'pass123'
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Username is required'

    def test_missing_first_name(self, client):
        res = client.post('/api/auth/signup', json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'pass123'
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'First name is required'

    def test_missing_email(self, client):
        res = client.post('/api/auth/signup', json={
            'username': 'alice',
            'first_name': 'Alice',
            'password': 'pass123'
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Email is required'

    def test_missing_password(self, client):
        res = client.post('/api/auth/signup', json={
            'username': 'alice',
            'first_name': 'Alice',
            'email': 'alice@example.com'
        })
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Password is required'

    def test_empty_body(self, client):
        res = client.post('/api/auth/signup', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Username is required'

    def test_duplicate_username(self, client):
        payload = {'username': 'alice', 'first_name': 'Alice', 'email': 'alice@example.com', 'password': 'pass123'}
        client.post('/api/auth/signup', json=payload)

        res = client.post('/api/auth/signup', json={
            'username': 'alice',
            'first_name': 'Alice',
            'email': 'other@example.com',
            'password': 'pass123'
        })
        assert res.status_code == 409
        assert res.get_json()['error'] == 'Username already exists'

    def test_duplicate_email(self, client):
        payload = {'username': 'alice', 'first_name': 'Alice', 'email': 'alice@example.com', 'password': 'pass123'}
        client.post('/api/auth/signup', json=payload)

        res = client.post('/api/auth/signup', json={
            'username': 'bob',
            'first_name': 'Bob',
            'email': 'alice@example.com',
            'password': 'pass123'
        })
        assert res.status_code == 409
        assert res.get_json()['error'] == 'Email already in use'


class TestLogin:

    def test_valid_login(self, client, registered_user):
        res = client.post('/api/auth/login', json={
            'username': registered_user['username'],
            'password': registered_user['password']
        })
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Login successful'
        assert res.get_json()['first_name'] == registered_user['first_name']

    def test_wrong_password(self, client, registered_user):
        res = client.post('/api/auth/login', json={
            'username': registered_user['username'],
            'password': 'wrongpassword'
        })
        assert res.status_code == 401
        assert res.get_json()['error'] == 'Invalid username or password'

    def test_unknown_user(self, client):
        res = client.post('/api/auth/login', json={
            'username': 'nobody',
            'password': 'pass123'
        })
        assert res.status_code == 401
        assert res.get_json()['error'] == 'Invalid username or password'

    def test_missing_username(self, client):
        res = client.post('/api/auth/login', json={'password': 'pass123'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Username is required'

    def test_missing_password(self, client):
        res = client.post('/api/auth/login', json={'username': 'alice'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Password is required'

    def test_empty_body(self, client):
        res = client.post('/api/auth/login', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Username is required'
