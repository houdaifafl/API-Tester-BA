class TestCreateRequest:

    def _collection_id(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        return auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']

    def _get_requests_in_collection(self, auth_client, auth_data, col_id):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        col = next(c for c in cols if c['id'] == col_id)
        return col['requests']

    def test_creates_request(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        res = auth_client.post(f'/api/collections/{col_id}/requests')
        assert res.status_code == 201

    def test_default_name(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        req = auth_client.post(f'/api/collections/{col_id}/requests').get_json()
        assert req['name'] == 'New Request'

    def test_default_method(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        req = auth_client.post(f'/api/collections/{col_id}/requests').get_json()
        assert req['method'] == 'GET'

    def test_default_url(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        req = auth_client.post(f'/api/collections/{col_id}/requests').get_json()
        assert req['url'] == ''

    def test_response_has_id_and_collection_id(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        req = auth_client.post(f'/api/collections/{col_id}/requests').get_json()
        assert 'id' in req and req['id'] is not None
        assert req['collection_id'] == col_id

    def test_new_request_appears_in_collection(self, auth_client, auth_data):
        col_id = self._collection_id(auth_client, auth_data)
        req_id = auth_client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        ids = [r['id'] for r in self._get_requests_in_collection(auth_client, auth_data, col_id)]
        assert req_id in ids

    def test_non_existent_collection_returns_404(self, auth_client):
        res = auth_client.post('/api/collections/9999/requests')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Collection not found'


class TestRenameRequest:

    def _create_request(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        return auth_client.post(f'/api/collections/{col_id}/requests').get_json()

    def test_renames_request(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'name': 'Login Test'})
        assert res.status_code == 200
        assert res.get_json()['name'] == 'Login Test'

    def test_rename_response_contains_id_and_name(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        data = auth_client.patch(f'/api/requests/{req_id}', json={'name': 'Named'}).get_json()
        assert 'id' in data
        assert 'name' in data

    def test_rename_reflected_in_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        req_id = auth_client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        auth_client.patch(f'/api/requests/{req_id}', json={'name': 'Updated Name'})
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        names = [r['name'] for c in cols for r in c['requests']]
        assert 'Updated Name' in names

    def test_empty_name_falls_through_to_400(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'name': ''})
        assert res.status_code == 400

    def test_non_existent_request_returns_404(self, auth_client):
        res = auth_client.patch('/api/requests/9999', json={'name': 'Ghost'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Request not found'


class TestUpdateRequestMethod:

    def _create_request(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        return auth_client.post(f'/api/collections/{col_id}/requests').get_json()

    def test_updates_to_post(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'POST'})
        assert res.status_code == 200
        assert res.get_json()['method'] == 'POST'

    def test_updates_to_put(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'PUT'})
        assert res.status_code == 200
        assert res.get_json()['method'] == 'PUT'

    def test_updates_to_delete(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'DELETE'})
        assert res.status_code == 200
        assert res.get_json()['method'] == 'DELETE'

    def test_updates_back_to_get(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        auth_client.patch(f'/api/requests/{req_id}', json={'method': 'POST'})
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'GET'})
        assert res.status_code == 200
        assert res.get_json()['method'] == 'GET'

    def test_response_contains_id_and_method(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        data = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'POST'}).get_json()
        assert 'id' in data
        assert 'method' in data

    def test_method_reflected_in_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        req_id = auth_client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        auth_client.patch(f'/api/requests/{req_id}', json={'method': 'PUT'})
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        methods = [r['method'] for c in cols for r in c['requests'] if r['id'] == req_id]
        assert methods[0] == 'PUT'

    def test_invalid_method_returns_400(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'method': 'INVALID'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invalid method'

    def test_non_existent_request_returns_404(self, auth_client):
        res = auth_client.patch('/api/requests/9999', json={'method': 'POST'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Request not found'


class TestSaveRequest:

    def _create_request(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        return auth_client.post(f'/api/collections/{col_id}/requests').get_json()

    def _find_request(self, auth_client, auth_data, req_id):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        for col in cols:
            for r in col['requests']:
                if r['id'] == req_id:
                    return r
        return None

    def test_saves_url(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'url': 'https://api.example.com/users'})
        assert res.status_code == 200
        assert self._find_request(auth_client, auth_data, req_id)['url'] == 'https://api.example.com/users'

    def test_saves_params(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        params = [{'key': 'page', 'value': '1'}]
        auth_client.patch(f'/api/requests/{req_id}', json={'params': params})
        assert self._find_request(auth_client, auth_data, req_id)['params'] == params

    def test_saves_headers(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        headers = [{'key': 'Accept', 'value': 'application/json'}]
        auth_client.patch(f'/api/requests/{req_id}', json={'headers': headers})
        assert self._find_request(auth_client, auth_data, req_id)['headers'] == headers

    def test_saves_body(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        body = {'type': 'raw', 'content': '{"key": "value"}'}
        auth_client.patch(f'/api/requests/{req_id}', json={'body': body})
        assert self._find_request(auth_client, auth_data, req_id)['body'] == body

    def test_saves_auth(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        auth = {'type': 'bearer', 'token': 'abc123'}
        auth_client.patch(f'/api/requests/{req_id}', json={'auth': auth})
        assert self._find_request(auth_client, auth_data, req_id)['auth'] == auth

    def test_saves_multiple_fields_at_once(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        auth_client.patch(f'/api/requests/{req_id}', json={
            'url': 'https://api.example.com',
            'params': [{'key': 'q', 'value': 'test'}],
            'headers': [{'key': 'X-Token', 'value': 'xyz'}],
        })
        saved = self._find_request(auth_client, auth_data, req_id)
        assert saved['url'] == 'https://api.example.com'
        assert saved['params'] == [{'key': 'q', 'value': 'test'}]
        assert saved['headers'] == [{'key': 'X-Token', 'value': 'xyz'}]

    def test_partial_save_does_not_overwrite_other_fields(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        auth_client.patch(f'/api/requests/{req_id}', json={'url': 'https://api.example.com'})
        auth_client.patch(f'/api/requests/{req_id}', json={'params': [{'key': 'a', 'value': 'b'}]})
        saved = self._find_request(auth_client, auth_data, req_id)
        assert saved['url'] == 'https://api.example.com'
        assert saved['params'] == [{'key': 'a', 'value': 'b'}]

    def test_save_response_contains_only_id(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        data = auth_client.patch(f'/api/requests/{req_id}', json={'url': 'https://x.com'}).get_json()
        assert data == {'id': req_id}

    def test_no_valid_fields_returns_400(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'No valid fields provided'

    def test_name_takes_priority_over_save_fields(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.patch(f'/api/requests/{req_id}', json={'name': 'Priority', 'url': 'https://x.com'})
        assert res.status_code == 200
        data = res.get_json()
        assert 'name' in data and data['name'] == 'Priority'
        assert 'url' not in data

    def test_non_existent_request_returns_404(self, auth_client):
        res = auth_client.patch('/api/requests/9999', json={'url': 'https://x.com'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Request not found'


class TestDeleteRequest:

    def _create_request(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        return auth_client.post(f'/api/collections/{col_id}/requests').get_json()

    def test_deletes_request(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        res = auth_client.delete(f'/api/requests/{req_id}')
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Request deleted'

    def test_deleted_request_not_in_collection(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        col_id = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()[0]['id']
        req_id = auth_client.post(f'/api/collections/{col_id}/requests').get_json()['id']
        auth_client.delete(f'/api/requests/{req_id}')
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        ids = [r['id'] for c in cols for r in c['requests']]
        assert req_id not in ids

    def test_non_existent_request_returns_404(self, auth_client):
        res = auth_client.delete('/api/requests/9999')
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Request not found'

    def test_double_delete_returns_404(self, auth_client, auth_data):
        req_id = self._create_request(auth_client, auth_data)['id']
        auth_client.delete(f'/api/requests/{req_id}')
        res = auth_client.delete(f'/api/requests/{req_id}')
        assert res.status_code == 404
