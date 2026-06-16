from unittest.mock import patch, MagicMock
import requests as requests_lib


def _mock_response(status_code=200, json_data=None, text='', raise_json=False):
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    if raise_json:
        mock.json.side_effect = ValueError('not json')
    else:
        mock.json.return_value = json_data if json_data is not None else {}
    return mock


class TestExecuteValidation:

    def test_missing_method_returns_400(self, client):
        res = client.post('/api/execute', json={'url': 'https://example.com'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Method and URL are required'

    def test_missing_url_returns_400(self, client):
        res = client.post('/api/execute', json={'method': 'GET'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Method and URL are required'

    def test_missing_both_returns_400(self, client):
        res = client.post('/api/execute', json={})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Method and URL are required'

    def test_non_json_body_returns_400(self, client):
        res = client.post('/api/execute', data='plain text', content_type='text/plain')
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Method and URL are required'


class TestExecuteSuccess:

    def _execute(self, client, **kwargs):
        payload = {'method': 'GET', 'url': 'https://example.com'}
        payload.update(kwargs)
        return client.post('/api/execute', json=payload)

    @patch('services.api_client_service.requests.request')
    def test_returns_status_code(self, mock_req, client):
        mock_req.return_value = _mock_response(status_code=200, json_data={'id': 1})
        data = self._execute(client).get_json()
        assert data['status'] == 200

    @patch('services.api_client_service.requests.request')
    def test_returns_non_200_status_code(self, mock_req, client):
        mock_req.return_value = _mock_response(status_code=404, json_data={'error': 'not found'})
        data = self._execute(client).get_json()
        assert data['status'] == 404

    @patch('services.api_client_service.requests.request')
    def test_returns_response_time(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        data = self._execute(client).get_json()
        assert 'response_time' in data
        assert isinstance(data['response_time'], float)

    @patch('services.api_client_service.requests.request')
    def test_returns_json_data(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={'key': 'value'})
        data = self._execute(client).get_json()
        assert data['data'] == {'key': 'value'}

    @patch('services.api_client_service.requests.request')
    def test_returns_text_when_response_is_not_json(self, mock_req, client):
        mock_req.return_value = _mock_response(text='plain response', raise_json=True)
        data = self._execute(client).get_json()
        assert data['data'] == 'plain response'

    @patch('services.api_client_service.requests.request')
    def test_lowercase_method_is_uppercased(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        client.post('/api/execute', json={'method': 'get', 'url': 'https://example.com'})
        assert mock_req.call_args[1]['method'] == 'GET'

    @patch('services.api_client_service.requests.request')
    def test_dict_body_sent_as_json(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client, method='POST', body={'name': 'test'})
        call_kwargs = mock_req.call_args[1]
        assert call_kwargs['json'] == {'name': 'test'}
        assert 'data' not in call_kwargs

    @patch('services.api_client_service.requests.request')
    def test_list_body_sent_as_json(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client, method='POST', body=[{'id': 1}, {'id': 2}])
        call_kwargs = mock_req.call_args[1]
        assert call_kwargs['json'] == [{'id': 1}, {'id': 2}]
        assert 'data' not in call_kwargs

    @patch('services.api_client_service.requests.request')
    def test_string_body_sent_as_raw_data(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client, method='POST', body='raw string')
        call_kwargs = mock_req.call_args[1]
        assert call_kwargs['data'] == 'raw string'
        assert 'json' not in call_kwargs

    @patch('services.api_client_service.requests.request')
    def test_no_body_sends_no_body_kwargs(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client)
        call_kwargs = mock_req.call_args[1]
        assert 'json' not in call_kwargs
        assert 'data' not in call_kwargs

    @patch('services.api_client_service.requests.request')
    def test_params_forwarded_to_request(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client, params={'page': '1', 'limit': '10'})
        assert mock_req.call_args[1]['params'] == {'page': '1', 'limit': '10'}

    @patch('services.api_client_service.requests.request')
    def test_headers_forwarded_to_request(self, mock_req, client):
        mock_req.return_value = _mock_response(json_data={})
        self._execute(client, headers={'Authorization': 'Bearer token123'})
        assert mock_req.call_args[1]['headers'] == {'Authorization': 'Bearer token123'}


class TestExecuteErrors:

    @patch('services.api_client_service.requests.request')
    def test_timeout_returns_504(self, mock_req, client):
        mock_req.side_effect = requests_lib.exceptions.Timeout()
        res = client.post('/api/execute', json={'method': 'GET', 'url': 'https://example.com'})
        assert res.status_code == 504
        assert res.get_json()['error'] == 'Request timed out'

    @patch('services.api_client_service.requests.request')
    def test_connection_error_returns_500(self, mock_req, client):
        mock_req.side_effect = requests_lib.exceptions.ConnectionError('connection refused')
        res = client.post('/api/execute', json={'method': 'GET', 'url': 'https://example.com'})
        assert res.status_code == 500
        assert 'error' in res.get_json()

    @patch('services.api_client_service.requests.request')
    def test_generic_request_exception_returns_500(self, mock_req, client):
        mock_req.side_effect = requests_lib.exceptions.RequestException('something went wrong')
        res = client.post('/api/execute', json={'method': 'GET', 'url': 'https://example.com'})
        assert res.status_code == 500
        assert 'error' in res.get_json()
