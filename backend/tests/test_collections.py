class TestListCollections:

    def test_returns_default_collection(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.get(f'/api/workspaces/{ws_id}/collections')
        assert res.status_code == 200
        cols = res.get_json()
        assert len(cols) == 1
        assert cols[0]['is_default'] is True

    def test_default_collection_has_correct_name(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        assert col['name'] == 'My Collection'

    def test_collection_items_have_all_fields(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]
        assert 'id' in col
        assert 'name' in col
        assert 'is_default' in col
        assert 'requests' in col

    def test_seeded_requests_have_all_fields(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        requests = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['requests']
        for r in requests:
            assert 'id' in r
            assert 'name' in r
            assert 'method' in r
            assert 'url' in r

    def test_default_collection_has_two_seeded_requests(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        requests = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['requests']
        assert len(requests) == 2
        names = [r['name'] for r in requests]
        methods = [r['method'] for r in requests]
        assert 'Get data' in names
        assert 'Post data' in names
        assert 'GET' in methods
        assert 'POST' in methods

    def test_returns_all_collections(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        client.post(f'/api/workspaces/{ws_id}/collections')
        client.post(f'/api/workspaces/{ws_id}/collections')
        cols = client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        assert len(cols) == 3

    def test_ensure_default_is_idempotent(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        client.get(f'/api/workspaces/{ws_id}/collections')
        client.get(f'/api/workspaces/{ws_id}/collections')
        cols = client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        default_cols = [c for c in cols if c['is_default']]
        assert len(default_cols) == 1


class TestCreateCollection:

    def test_creates_collection(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = client.post(f'/api/workspaces/{ws_id}/collections')
        assert res.status_code == 201

    def test_new_collection_default_name(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['name'] == 'New Collection'

    def test_new_collection_is_not_default(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['is_default'] is False

    def test_new_collection_has_empty_requests(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert col['requests'] == []

    def test_new_collection_has_id(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        assert 'id' in col and col['id'] is not None

    def test_new_collection_appears_in_list(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col = client.post(f'/api/workspaces/{ws_id}/collections').get_json()
        col_ids = [c['id'] for c in client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert col['id'] in col_ids


class TestRenameCollection:

    def _get_non_default_collection(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        return client.post(f'/api/workspaces/{ws_id}/collections').get_json()

    def test_renames_collection(self, client, auth_data):
        col_id = self._get_non_default_collection(client, auth_data)['id']
        res = client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed'})
        assert res.status_code == 200
        assert res.get_json()['name'] == 'Renamed'

    def test_rename_response_contains_full_collection(self, client, auth_data):
        col_id = self._get_non_default_collection(client, auth_data)['id']
        data = client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed'}).get_json()
        assert 'id' in data
        assert 'name' in data
        assert 'is_default' in data
        assert 'requests' in data

    def test_rename_reflected_in_list(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._get_non_default_collection(client, auth_data)['id']
        client.patch(f'/api/collections/{col_id}', json={'name': 'Updated Name'})
        names = [c['name'] for c in client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert 'Updated Name' in names

    def test_can_rename_default_collection(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        res = client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed Default'})
        assert res.status_code == 200
        assert res.get_json()['name'] == 'Renamed Default'

    def test_missing_name_returns_400(self, client, auth_data):
        col_id = self._get_non_default_collection(client, auth_data)['id']
        res = client.patch(f'/api/collections/{col_id}', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'name is required'

    def test_empty_name_returns_400(self, client, auth_data):
        col_id = self._get_non_default_collection(client, auth_data)['id']
        res = client.patch(f'/api/collections/{col_id}', json={'name': ''})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'name is required'

    def test_non_existent_collection_returns_404(self, client):
        res = client.patch('/api/collections/9999', json={'name': 'Ghost'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Collection not found'


class TestDeleteCollection:

    def _create_non_default(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        return client.post(f'/api/workspaces/{ws_id}/collections').get_json()

    def test_deletes_collection(self, client, auth_data):
        col_id = self._create_non_default(client, auth_data)['id']
        res = client.delete(f'/api/collections/{col_id}')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Collection deleted'

    def test_deleted_collection_not_in_list(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._create_non_default(client, auth_data)['id']
        client.delete(f'/api/collections/{col_id}')
        col_ids = [c['id'] for c in client.get(f'/api/workspaces/{ws_id}/collections').get_json()]
        assert col_id not in col_ids

    def test_cannot_delete_default_collection(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        res = client.delete(f'/api/collections/{col_id}')
        assert res.status_code == 403
        assert 'default' in res.get_json()['error'].lower()

    def test_non_existent_collection_returns_404(self, client):
        res = client.delete('/api/collections/9999')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Collection not found'

    def test_deleting_collection_cascades_to_requests(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = self._create_non_default(client, auth_data)['id']
        req_id = client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        client.delete(f'/api/collections/{col_id}')
        res = client.patch(f'/api/requests/{req_id}', json={'name': 'ghost'})
        assert res.status_code == 404
