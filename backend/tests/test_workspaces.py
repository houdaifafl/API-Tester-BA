from tests.conftest import signup_and_login


class TestListWorkspaces:

    def test_returns_default_workspace_after_signup(self, auth_client):
        res = auth_client.get('/api/workspaces')
        assert res.status_code == 200
        workspaces = res.get_json()
        assert len(workspaces) == 1
        assert workspaces[0]['is_default'] is True

    def test_missing_token_returns_401(self, client):
        res = client.get('/api/workspaces')
        assert res.status_code == 401
        assert 'token is missing' in res.get_json()['error'].lower()

    def test_unknown_user_returns_empty_list(self, client):
        from services.jwt_service import encode_token
        token = encode_token({'user_id': 9999})
        res = client.get('/api/workspaces', headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_all_workspaces_for_user(self, auth_client):
        auth_client.post('/api/workspaces', json={'name': 'Second WS'})
        auth_client.post('/api/workspaces', json={'name': 'Third WS'})
        res = auth_client.get('/api/workspaces')
        assert res.status_code == 200
        assert len(res.get_json()) == 3

    def test_does_not_return_other_users_workspaces(self, client, auth_client):
        other = signup_and_login(client, 'other', 'other@example.com')
        other_token = other['token']
        client.post('/api/workspaces', json={'name': 'Other WS'}, headers={'Authorization': f'Bearer {other_token}'})
        res = auth_client.get('/api/workspaces')
        names = [w['name'] for w in res.get_json()]
        assert 'Other WS' not in names

    def test_list_items_contain_all_fields(self, auth_client):
        workspaces = auth_client.get('/api/workspaces').get_json()
        for w in workspaces:
            assert 'id' in w
            assert 'name' in w
            assert 'is_default' in w

    def test_invalid_token_returns_401(self, client):
        res = client.get('/api/workspaces', headers={'Authorization': 'Bearer invalid'})
        assert res.status_code == 401
        assert 'unauthorized' in res.get_json()['error'].lower()


class TestCreateWorkspace:

    def test_creates_workspace_with_correct_fields(self, auth_client):
        res = auth_client.post('/api/workspaces', json={'name': 'My API Tests'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['name'] == 'My API Tests'
        assert data['is_default'] is False
        assert 'id' in data

    def test_new_workspace_appears_in_list(self, auth_client):
        auth_client.post('/api/workspaces', json={'name': 'Second WS'})
        res = auth_client.get('/api/workspaces')
        assert len(res.get_json()) == 2

    def test_missing_token_returns_401(self, client):
        res = client.post('/api/workspaces', json={'name': 'No User'})
        assert res.status_code == 401

    def test_missing_name_returns_400(self, auth_client):
        res = auth_client.post('/api/workspaces', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Workspace name is required'

    def test_empty_body_returns_400(self, auth_client):
        res = auth_client.post('/api/workspaces', json={})
        assert res.status_code == 400

    def test_new_workspace_seeds_default_collection(self, auth_client):
        create_res = auth_client.post('/api/workspaces', json={'name': 'New WS'})
        ws_id = create_res.get_json()['id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        assert len(cols) == 1
        assert cols[0]['name'] == 'My Collection'
        assert cols[0]['is_default'] is True

    def test_seeded_collection_contains_default_requests(self, auth_client):
        create_res = auth_client.post('/api/workspaces', json={'name': 'New WS'})
        ws_id = create_res.get_json()['id']
        col = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        request_names = [r['name'] for r in col['requests']]
        request_methods = [r['method'] for r in col['requests']]
        assert len(col['requests']) == 2
        assert 'Get data' in request_names
        assert 'Post data' in request_names
        assert 'GET' in request_methods
        assert 'POST' in request_methods


class TestGetWorkspace:

    def test_returns_correct_workspace(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.get(f'/api/workspaces/{ws_id}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['id'] == ws_id
        assert data['is_default'] is True
        assert 'name' in data
        assert isinstance(data['name'], str) and len(data['name']) > 0

    def test_not_found_returns_404(self, auth_client):
        res = auth_client.get('/api/workspaces/9999')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Workspace not found'

    def test_other_users_workspace_returns_403(self, client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        other_token = other['token']
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_missing_token_returns_401(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}')
        assert res.status_code == 401

    def test_invalid_id_format_returns_400(self, auth_client):
        res = auth_client.get('/api/workspaces/abc')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invalid workspace ID'


class TestDeleteWorkspace:

    def test_deletes_non_default_workspace(self, auth_client):
        create_res = auth_client.post('/api/workspaces', json={'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        res = auth_client.delete(f'/api/workspaces/{ws_id}')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Workspace deleted'

    def test_deleted_workspace_no_longer_listed(self, auth_client):
        create_res = auth_client.post('/api/workspaces', json={'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        auth_client.delete(f'/api/workspaces/{ws_id}')
        listed_ids = [w['id'] for w in auth_client.get('/api/workspaces').get_json()]
        assert ws_id not in listed_ids

    def test_cannot_delete_default_workspace(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.delete(f'/api/workspaces/{ws_id}')
        assert res.status_code == 403
        assert 'default' in res.get_json()['error'].lower()

    def test_not_found_returns_404(self, auth_client):
        res = auth_client.delete('/api/workspaces/9999')
        assert res.status_code == 404

    def test_wrong_user_cannot_delete(self, client, auth_client, auth_data):
        other = signup_and_login(client, 'other', 'other@example.com')
        other_token = other['token']
        create_res = auth_client.post('/api/workspaces', json={'name': 'Protected WS'})
        ws_id = create_res.get_json()['id']
        res = client.delete(f'/api/workspaces/{ws_id}', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 404

    def test_missing_token_returns_401(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}')
        assert res.status_code == 401

    def test_invalid_token_returns_401(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}', headers={'Authorization': 'Bearer invalid'})
        assert res.status_code == 401

    def test_deleting_workspace_cascades_to_collections(self, auth_client):
        create_res = auth_client.post('/api/workspaces', json={'name': 'Temp WS'})
        ws_id = create_res.get_json()['id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        auth_client.delete(f'/api/workspaces/{ws_id}')
        res = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'ghost'})
        assert res.status_code == 404


class TestLeaveWorkspace:

    def _create_member_client(self, client, owner_client, ws_id, role='editor'):
        """Helper: sign up a second user, invite them, accept, return their client."""
        other = signup_and_login(client, 'member_user', 'member@example.com')
        other_token = other['token']
        owner_client.post(
            f'/api/workspaces/{ws_id}/invitations',
            json={'username': 'member_user', 'role': role}
        )
        # Get the pending invitation id
        inv_res = client.get('/api/invitations/pending',
                             headers={'Authorization': f'Bearer {other_token}'})
        inv_id = inv_res.get_json()[0]['id']
        client.post(f'/api/invitations/{inv_id}/accept',
                    headers={'Authorization': f'Bearer {other_token}'})
        return other_token

    def test_editor_can_leave_workspace(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_token = self._create_member_client(client, auth_client, ws_id, role='editor')
        res = client.delete(f'/api/workspaces/{ws_id}/leave',
                            headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        assert res.get_json()['message'] == 'You have left the workspace.'

    def test_viewer_can_leave_workspace(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_token = self._create_member_client(client, auth_client, ws_id, role='viewer')
        res = client.delete(f'/api/workspaces/{ws_id}/leave',
                            headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        assert res.get_json()['message'] == 'You have left the workspace.'

    def test_owner_cannot_leave_workspace(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.delete(f'/api/workspaces/{ws_id}/leave')
        assert res.status_code == 403
        assert 'owners' in res.get_json()['error'].lower()

    def test_non_member_leave_returns_404(self, client, auth_data):
        other = signup_and_login(client, 'stranger', 'stranger@example.com')
        other_token = other['token']
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}/leave',
                            headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 404

    def test_workspace_inaccessible_after_leave(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_token = self._create_member_client(client, auth_client, ws_id, role='editor')
        client.delete(f'/api/workspaces/{ws_id}/leave',
                      headers={'Authorization': f'Bearer {other_token}'})
        res = client.get(f'/api/workspaces/{ws_id}',
                         headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403

    def test_missing_token_returns_401(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.delete(f'/api/workspaces/{ws_id}/leave')
        assert res.status_code == 401

