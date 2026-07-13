class TestListCollections:

    def test_returns_default_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.get(f'/api/workspaces/{ws_id}/collections')
        assert res.status_code == 200
        cols = res.get_json()
        assert len(cols) == 1
        assert cols[0]['is_default'] is True

    def test_default_collection_has_correct_name(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        assert col['name'] == 'My Collection'

    def test_collection_items_have_all_fields(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        assert 'id' in col
        assert 'name' in col
        assert 'is_default' in col
        assert 'requests' in col

    def test_seeded_requests_have_all_fields(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        requests = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['requests']
        for r in requests:
            assert 'id' in r
            assert 'name' in r
            assert 'method' in r
            assert 'url' in r

    def test_default_collection_has_two_seeded_requests(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        requests = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['requests']
        assert len(requests) == 2
        names = [r['name'] for r in requests]
        methods = [r['method'] for r in requests]
        assert 'Get data' in names
        assert 'Post data' in names
        assert 'GET' in methods
        assert 'POST' in methods

    def test_returns_all_collections(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        auth_client.post(f'/api/workspaces/{ws_id}/collections')
        auth_client.post(f'/api/workspaces/{ws_id}/collections')
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        assert len(cols) == 3

    def test_ensure_default_is_idempotent(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        auth_client.get(f'/api/workspaces/{ws_id}/collections')
        auth_client.get(f'/api/workspaces/{ws_id}/collections')
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        default_cols = [c for c in cols if c['is_default']]
        assert len(default_cols) == 1

    def test_list_collections_unauthorized_fails(self, client, auth_data):
        client._cookies.clear()
        client.post('/api/auth/signup', json={
            'username': 'unauthorized_cols_user',
            'first_name': 'Unauthorized',
            'email': 'unauthorized_cols@example.com',
            'password': 'password123'
        })
        login_res = client.post('/api/auth/login', json={
            'username': 'unauthorized_cols_user',
            'password': 'password123'
        })
        token = login_res.get_json()['token']

        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}/collections', headers={'Authorization': f'Bearer {token}'})
        assert res.status_code == 403
        assert 'forbidden' in res.get_json()['error'].lower()

    def test_list_collections_nonexistent_workspace_fails(self, auth_client):
        res = auth_client.get('/api/workspaces/99999/collections')
        assert res.status_code == 404


class TestCreateCollection:

    def test_creates_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.post(f'/api/workspaces/{ws_id}/collections')
        assert res.status_code == 201

    def test_new_collection_default_name(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['name'] == 'New Collection'

    def test_new_collection_is_not_default(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['is_default'] is False

    def test_new_collection_has_empty_requests(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['requests'] == []

    def test_new_collection_has_id(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert 'id' in col and col['id'] is not None

    def test_new_collection_appears_in_list(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        col_ids = [c['id'] for c in auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert col['id'] in col_ids


class TestRenameCollection:

    def _get_non_default_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        return auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()

    def test_renames_collection(self, auth_client, auth_data):
        col_id = self._get_non_default_collection(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed'})
        assert res.status_code == 200
        assert res.get_json()['name'] == 'Renamed'

    def test_rename_response_contains_full_collection(self, auth_client, auth_data):
        col_id = self._get_non_default_collection(auth_client, auth_data)['id']
        data = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed'}).get_json()
        assert 'id' in data
        assert 'name' in data
        assert 'is_default' in data
        assert 'requests' in data

    def test_rename_reflected_in_list(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._get_non_default_collection(auth_client, auth_data)['id']
        auth_client.patch(f'/api/collections/{col_id}', json={'name': 'Updated Name'})
        names = [c['name'] for c in auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert 'Updated Name' in names

    def test_can_rename_default_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        res = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed Default'})
        assert res.status_code == 200
        assert res.get_json()['name'] == 'Renamed Default'

    def test_missing_name_returns_400(self, auth_client, auth_data):
        col_id = self._get_non_default_collection(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/collections/{col_id}', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'name is required'

    def test_empty_name_returns_400(self, auth_client, auth_data):
        col_id = self._get_non_default_collection(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/collections/{col_id}', json={'name': ''})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'name is required'

    def test_non_existent_collection_returns_404(self, auth_client):
        res = auth_client.patch('/api/collections/9999', json={'name': 'Ghost'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Collection not found'


class TestDeleteCollection:

    def _create_non_default(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        return auth_client.post(f'/api/workspaces/{ws_id}/collections').get_json()

    def test_deletes_collection(self, auth_client, auth_data):
        col_id = self._create_non_default(auth_client, auth_data)['id']
        res = auth_client.delete(f'/api/collections/{col_id}')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Collection deleted'

    def test_deleted_collection_not_in_list(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._create_non_default(auth_client, auth_data)['id']
        auth_client.delete(f'/api/collections/{col_id}')
        col_ids = [c['id'] for c in auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert col_id not in col_ids

    def test_cannot_delete_default_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        res = auth_client.delete(f'/api/collections/{col_id}')
        assert res.status_code == 403
        assert 'default' in res.get_json()['error'].lower()

    def test_non_existent_collection_returns_404(self, auth_client):
        res = auth_client.delete('/api/collections/9999')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Collection not found'

    def test_deleting_collection_cascades_to_requests(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._create_non_default(auth_client, auth_data)['id']
        req_id = auth_client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        auth_client.delete(f'/api/collections/{col_id}')
        res = auth_client.patch(f'/api/requests/{req_id}', json={'name': 'ghost'})
        assert res.status_code == 404
