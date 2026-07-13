import pytest
from models.base import db
from models.history_model import History
from models.workspace_model import Workspace
from sqlalchemy import text

class TestHistoryEncryption:

    def test_history_db_is_encrypted(self, client, app):
        # Create a workspace
        with app.app_context():
            ws = Workspace(name="Test Encryption Workspace", user_id=1)
            db.session.add(ws)
            db.session.commit()
            workspace_id = ws.id

        # Insert a history entry with secret data
        secret_headers = {"Authorization": "Bearer super-secret-token-123"}
        secret_auth = {"type": "bearer", "bearer": {"token": "super-secret-token-123"}}
        secret_params = {"key": "secret-value"}
        secret_body = {"password": "admin-password"}
        secret_data = {"token": "returned-session-token"}

        with app.app_context():
            entry = History(
                workspace_id=workspace_id,
                method="POST",
                url="https://api.example.com/login",
                params=secret_params,
                headers=secret_headers,
                body=secret_body,
                auth=secret_auth,
                status=200,
                response_time=0.45,
                data=secret_data
            )
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id

        # 1. Direct SQL Query to assert data is encrypted at rest (not plaintext JSON)
        with app.app_context():
            result = db.session.execute(
                text("SELECT headers, auth, params, body, data FROM history WHERE id = :id"),
                {"id": entry_id}
            ).fetchone()
            
            raw_headers, raw_auth, raw_params, raw_body, raw_data = result
            
            # Fernet tokens start with "gAAAA"
            assert raw_headers.startswith("gAAAA")
            assert raw_auth.startswith("gAAAA")
            assert raw_params.startswith("gAAAA")
            assert raw_body.startswith("gAAAA")
            assert raw_data.startswith("gAAAA")

            # Check that raw DB strings do not contain plaintext secrets
            assert "super-secret-token-123" not in raw_headers
            assert "admin-password" not in raw_body
            assert "returned-session-token" not in raw_data

        # 2. Assert ORM model load decrypts transparently
        with app.app_context():
            loaded = db.session.get(History, entry_id)
            assert loaded.headers == secret_headers
            assert loaded.auth == secret_auth
            assert loaded.params == secret_params
            assert loaded.body == secret_body
            assert loaded.data == secret_data

    def test_history_api_masks_sensitive_data(self, client, app):
        client._cookies.clear()
        
        # Sign up and log in
        client.post('/api/auth/signup', json={
            'username': 'historyuser',
            'first_name': 'History',
            'email': 'historyuser@example.com',
            'password': 'password123'
        })
        client.post('/api/auth/login', json={
            'username': 'historyuser',
            'password': 'password123'
        })

        # Get default workspace
        ws_res = client.get('/api/workspaces')
        assert ws_res.status_code == 200
        workspace_id = ws_res.get_json()[0]['id']

        # Create history entry through the API
        secret_headers = {"Authorization": "Bearer super-secret-token-123", "Content-Type": "application/json"}
        secret_auth = {"type": "bearer", "bearer": {"token": "super-secret-token-123"}}
        
        create_res = client.post(f'/api/workspaces/{workspace_id}/history', json={
            'method': 'POST',
            'url': 'https://api.example.com/v1/auth',
            'headers': secret_headers,
            'auth': secret_auth,
            'status': 200,
            'response_time': 0.12,
            'data': {'token': 'secret-response-session-token'}
        })
        assert create_res.status_code == 201
        created_data = create_res.get_json()

        # Assert response masks headers and auth, and hides response body
        assert created_data['headers']['Authorization'] == 'Bearer ****'
        assert created_data['headers']['Content-Type'] == 'application/json'
        assert created_data['auth']['bearer']['token'] == '****'
        assert 'Response body not stored due to security policy' in created_data['data']['message']

        # Verify reading history back from the list endpoint is also masked
        list_res = client.get(f'/api/workspaces/{workspace_id}/history')
        assert list_res.status_code == 200
        history_list = list_res.get_json()
        assert len(history_list) >= 1
        
        entry = history_list[0]
        assert entry['headers']['Authorization'] == 'Bearer ****'
        assert entry['auth']['bearer']['token'] == '****'
        assert 'Response body not stored due to security policy' in entry['data']['message']
