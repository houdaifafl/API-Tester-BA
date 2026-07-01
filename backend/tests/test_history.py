import pytest
from tests.conftest import signup_and_login

class TestCreateHistory:
    def test_create_history_success(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        payload = {
            'method': 'POST',
            'url': 'https://api.example.com/data',
            'headers': [{'key': 'Content-Type', 'value': 'application/json'}],
            'params': [{'key': 'q', 'value': 'test'}],
            'body': {'foo': 'bar'},
            'auth': {'type': 'bearer', 'token': 'xyz'},
            'status': 200,
            'response_time': 150.5,
            'data': {'success': True}
        }
        res = auth_client.post(f'/api/workspaces/{ws_id}/history', json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert 'id' in data
        assert data['workspace_id'] == ws_id
        assert data['method'] == 'POST'
        assert data['url'] == 'https://api.example.com/data'
        assert data['headers'] == [{'key': 'Content-Type', 'value': 'application/json'}]
        assert data['params'] == [{'key': 'q', 'value': 'test'}]
        assert data['body'] == {'foo': 'bar'}
        assert data['auth'] == {'type': 'bearer', 'token': 'xyz'}
        assert data['status'] == 200
        assert data['response_time'] == 150.5
        assert data['data'] == {'success': True}
        assert 'created_at' in data

    def test_create_history_missing_fields(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.post(f'/api/workspaces/{ws_id}/history', json={'url': 'https://api.example.com/data'})
        assert res.status_code == 400
        assert 'method' in res.get_json()['error'].lower()

        res = auth_client.post(f'/api/workspaces/{ws_id}/history', json={'method': 'GET'})
        assert res.status_code == 400
        assert 'url' in res.get_json()['error'].lower()

    def test_create_history_missing_token(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.post(f'/api/workspaces/{ws_id}/history', json={'method': 'GET', 'url': 'http://example.com'})
        assert res.status_code == 401

    def test_create_history_forbidden_workspace(self, client, auth_client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        other_token = other['token']
        ws_id = auth_data['default_workspace_id'] # user's default workspace
        
        # 'other' user tries to write to our history
        res = client.post(f'/api/workspaces/{ws_id}/history', 
                          json={'method': 'GET', 'url': 'http://example.com'}, 
                          headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403
        assert 'forbidden' in res.get_json()['error'].lower()

    def test_create_history_not_found_workspace(self, auth_client):
        res = auth_client.post('/api/workspaces/99999/history', json={'method': 'GET', 'url': 'http://example.com'})
        assert res.status_code == 404
        assert 'not found' in res.get_json()['error'].lower()


class TestListHistory:
    def test_list_history_success_and_ordering(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # Create multiple entries to test order
        for i in range(5):
            res = auth_client.post(f'/api/workspaces/{ws_id}/history', json={
                'method': 'GET',
                'url': f'http://example.com/api/{i}'
            })
            assert res.status_code == 201

        res = auth_client.get(f'/api/workspaces/{ws_id}/history')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 5
        
        # Verify chronological descending order (latest first)
        assert data[0]['url'] == 'http://example.com/api/4'
        assert data[1]['url'] == 'http://example.com/api/3'
        assert data[2]['url'] == 'http://example.com/api/2'
        assert data[3]['url'] == 'http://example.com/api/1'
        assert data[4]['url'] == 'http://example.com/api/0'

    def test_list_history_limit_100(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # Create 105 entries
        for i in range(105):
            res = auth_client.post(f'/api/workspaces/{ws_id}/history', json={
                'method': 'GET',
                'url': f'http://example.com/api/{i}'
            })
            assert res.status_code == 201

        res = auth_client.get(f'/api/workspaces/{ws_id}/history')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data) == 100
        
        # The latest created should be index 0 (104), and oldest returned should be index 99 (5)
        assert data[0]['url'] == 'http://example.com/api/104'
        assert data[99]['url'] == 'http://example.com/api/5'

    def test_list_history_missing_token(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}/history')
        assert res.status_code == 401

    def test_list_history_forbidden_workspace(self, client, auth_client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        other_token = other['token']
        ws_id = auth_data['default_workspace_id']
        
        res = client.get(f'/api/workspaces/{ws_id}/history', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403
        assert 'forbidden' in res.get_json()['error'].lower()

    def test_list_history_not_found_workspace(self, auth_client):
        res = auth_client.get('/api/workspaces/99999/history')
        assert res.status_code == 404
