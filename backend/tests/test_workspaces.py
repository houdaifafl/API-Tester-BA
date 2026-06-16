from tests.conftest import signup_and_login


class TestListWorkspaces:

    def test_returns_default_workspace_after_signup(self, client, auth_data):
        res = client.get(f'/api/workspaces?user_id={auth_data["user_id"]}')
        assert res.status_code == 200
        workspaces = res.get_json()
        assert len(workspaces) == 1
        assert workspaces[0]['is_default'] is True

    def test_missing_user_id_returns_400(self, client):
        res = client.get('/api/workspaces')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'

    def test_unknown_user_returns_empty_list(self, client):
        res = client.get('/api/workspaces?user_id=9999')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_workspaces_for_user(self, client, auth_data):
        client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Second WS'})
        client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Third WS'})
        res = client.get(f'/api/workspaces?user_id={auth_data["user_id"]}')
        assert res.status_code == 200
        assert len(res.get_json()) == 3

    def test_does_not_return_other_users_workspaces(self, client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        client.post('/api/workspaces', json={'user_id': other['user_id'], 'name': 'Other WS'})
        res = client.get(f'/api/workspaces?user_id={auth_data["user_id"]}')
        names = [w['name'] for w in res.get_json()]
        assert 'Other WS' not in names

    def test_list_items_contain_all_fields(self, client, auth_data):
        workspaces = client.get(f'/api/workspaces?user_id={auth_data["user_id"]}').get_json()
        for w in workspaces:
            assert 'id' in w
            assert 'name' in w
            assert 'is_default' in w

    def test_non_integer_user_id_returns_400(self, client):
        res = client.get('/api/workspaces?user_id=abc')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'


class TestCreateWorkspace:

    def test_creates_workspace_with_correct_fields(self, client, auth_data):
        res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'My API Tests'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['name'] == 'My API Tests'
        assert data['is_default'] is False
        assert 'id' in data

    def test_new_workspace_appears_in_list(self, client, auth_data):
        client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Second WS'})
        res = client.get(f'/api/workspaces?user_id={auth_data["user_id"]}')
        assert len(res.get_json()) == 2

    def test_missing_user_id_returns_400(self, client):
        res = client.post('/api/workspaces', json={'name': 'No User'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'

    def test_missing_name_returns_400(self, client, auth_data):
        res = client.post('/api/workspaces', json={'user_id': auth_data['user_id']})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Workspace name is required'

    def test_empty_body_returns_400(self, client):
        res = client.post('/api/workspaces', json={})
        assert res.status_code == 400

    def test_new_workspace_seeds_default_collection(self, client, auth_data):
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'New WS'})
        ws_id = create_res.get_json()['id']
        cols = client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        assert len(cols) == 1
        assert cols[0]['name'] == 'My Collection'
        assert cols[0]['is_default'] is True

    def test_seeded_collection_contains_default_requests(self, client, auth_data):
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'New WS'})
        ws_id = create_res.get_json()['id']
        col = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        request_names = [r['name'] for r in col['requests']]
        request_methods = [r['method'] for r in col['requests']]
        assert len(col['requests']) == 2
        assert 'Get data' in request_names
        assert 'Post data' in request_names
        assert 'GET' in request_methods
        assert 'POST' in request_methods


class TestGetWorkspace:

    def test_returns_correct_workspace(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}?user_id={auth_data["user_id"]}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['id'] == ws_id
        assert data['is_default'] is True
        assert 'name' in data
        assert isinstance(data['name'], str) and len(data['name']) > 0

    def test_not_found_returns_404(self, client, auth_data):
        res = client.get(f'/api/workspaces/9999?user_id={auth_data["user_id"]}')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Workspace not found'

    def test_other_users_workspace_returns_403(self, client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}?user_id={other["user_id"]}')
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_missing_user_id_returns_400(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'

    def test_invalid_id_format_returns_400(self, client, auth_data):
        res = client.get(f'/api/workspaces/abc?user_id={auth_data["user_id"]}')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invalid workspace ID'


class TestDeleteWorkspace:

    def test_deletes_non_default_workspace(self, client, auth_data):
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        res = client.delete(f'/api/workspaces/{ws_id}?user_id={auth_data["user_id"]}')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Workspace deleted'

    def test_deleted_workspace_no_longer_listed(self, client, auth_data):
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        client.delete(f'/api/workspaces/{ws_id}?user_id={auth_data["user_id"]}')
        listed_ids = [w['id'] for w in client.get(f'/api/workspaces?user_id={auth_data["user_id"]}').get_json()]
        assert ws_id not in listed_ids

    def test_cannot_delete_default_workspace(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}?user_id={auth_data["user_id"]}')
        assert res.status_code == 403
        assert 'default' in res.get_json()['error'].lower()

    def test_not_found_returns_404(self, client, auth_data):
        res = client.delete(f'/api/workspaces/9999?user_id={auth_data["user_id"]}')
        assert res.status_code == 404

    def test_wrong_user_cannot_delete(self, client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Protected WS'})
        ws_id = create_res.get_json()['id']
        res = client.delete(f'/api/workspaces/{ws_id}?user_id={other["user_id"]}')
        assert res.status_code == 404

    def test_missing_user_id_returns_400(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'

    def test_non_integer_user_id_returns_400(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}?user_id=abc')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'user_id is required'

    def test_deleting_workspace_cascades_to_collections(self, client, auth_data):
        create_res = client.post('/api/workspaces', json={'user_id': auth_data['user_id'], 'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        col_id = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        client.delete(f'/api/workspaces/{ws_id}?user_id={auth_data["user_id"]}')
        res = client.patch(f'/api/collections/{col_id}', json={'name': 'ghost'})
        assert res.status_code == 404
