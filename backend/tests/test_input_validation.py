import pytest

class TestInputValidation:

    def test_signup_validation(self, client):
        # Long username
        res = client.post('/api/auth/signup', json={
            'username': 'a' * 101,
            'first_name': 'Test',
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert res.status_code == 400
        assert 'username' in res.get_json()['error'].lower()

        # Long first_name
        res = client.post('/api/auth/signup', json={
            'username': 'test_user',
            'first_name': 'a' * 101,
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert res.status_code == 400
        assert 'first name' in res.get_json()['error'].lower()

        # Long email
        res = client.post('/api/auth/signup', json={
            'username': 'test_user',
            'first_name': 'Test',
            'email': 'a' * 256 + '@example.com',
            'password': 'password123'
        })
        assert res.status_code == 400
        assert 'email' in res.get_json()['error'].lower()

        # Long password
        res = client.post('/api/auth/signup', json={
            'username': 'test_user',
            'first_name': 'Test',
            'email': 'test@example.com',
            'password': 'p' * 73
        })
        assert res.status_code == 400
        assert 'password' in res.get_json()['error'].lower()

    def test_login_validation(self, client):
        # Long username
        res = client.post('/api/auth/login', json={
            'username': 'a' * 101,
            'password': 'password123'
        })
        assert res.status_code == 400
        assert 'username' in res.get_json()['error'].lower()

        # Long password
        res = client.post('/api/auth/login', json={
            'username': 'test_user',
            'password': 'p' * 73
        })
        assert res.status_code == 400
        assert 'password' in res.get_json()['error'].lower()

    def test_workspace_name_validation(self, auth_client):
        res = auth_client.post('/api/workspaces', json={'name': 'a' * 101})
        assert res.status_code == 400
        assert 'workspace name' in res.get_json()['error'].lower()

    def test_collection_name_validation(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        col_id = cols[0]['id']

        res = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'a' * 101})
        assert res.status_code == 400
        assert 'collection name' in res.get_json()['error'].lower()

    def test_request_validation(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        col_id = cols[0]['id']

        # First create a request
        req = auth_client.post(f'/api/collections/{col_id}/requests').get_json()
        req_id = req['id']

        # Long name
        res = auth_client.patch(f'/api/requests/{req_id}', json={'name': 'a' * 101})
        assert res.status_code == 400
        assert 'request name' in res.get_json()['error'].lower()

        # Long method
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'A' * 11})
        assert res.status_code == 400
        assert 'request method' in res.get_json()['error'].lower()

        # Long URL
        res = auth_client.patch(f'/api/requests/{req_id}', json={'url': 'h' * 501})
        assert res.status_code == 400
        assert 'url' in res.get_json()['error'].lower()

    def test_comment_validation(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']

        # Long content
        res = auth_client.post(f'/api/workspaces/{ws_id}/comments', json={
            'content': 'c' * 2001
        })
        assert res.status_code == 400
        assert 'content' in res.get_json()['error'].lower()

        # Long target_tab
        res = auth_client.post(f'/api/workspaces/{ws_id}/comments', json={
            'content': 'Valid content',
            'target_tab': 't' * 51
        })
        assert res.status_code == 400
        assert 'target tab' in res.get_json()['error'].lower()

        # Long target_key
        res = auth_client.post(f'/api/workspaces/{ws_id}/comments', json={
            'content': 'Valid content',
            'target_key': 'k' * 256
        })
        assert res.status_code == 400
        assert 'target key' in res.get_json()['error'].lower()

    def test_execute_validation(self, auth_client):
        # Long method
        res = auth_client.post('/api/execute', json={
            'method': 'A' * 11,
            'url': 'http://example.com'
        })
        assert res.status_code == 400
        assert 'method' in res.get_json()['error'].lower()

        # Long url
        res = auth_client.post('/api/execute', json={
            'method': 'GET',
            'url': 'h' * 2049
        })
        assert res.status_code == 400
        assert 'url' in res.get_json()['error'].lower()

    def test_invitation_validation(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']

        # Long username
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={
            'username': 'u' * 101,
            'role': 'viewer'
        })
        assert res.status_code == 400
        assert 'username' in res.get_json()['error'].lower()

        # Long role
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={
            'username': 'invitee',
            'role': 'r' * 21
        })
        assert res.status_code == 400
        assert 'role' in res.get_json()['error'].lower()
