import pytest
from tests.conftest import signup_and_login
from models.base import db
from models.activity_model import WorkspaceActivity

class TestWorkspaceActivities:

    def test_get_activities_success(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.get(f'/api/workspaces/{ws_id}/activities')
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        # Should have at least the workspace creation/default collection creation events
        assert len(data) >= 1
        assert all(isinstance(x['user_username'], str) for x in data)

    def test_get_activities_forbidden(self, client, auth_data):
        other = signup_and_login(client, 'other_act', 'other_act@example.com')
        other_token = other['token']
        ws_id = auth_data['default_workspace_id']
        
        # Unauthorized access attempt
        res = client.get(f'/api/workspaces/{ws_id}/activities', 
                         headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403

    def test_activity_logging_on_collection_crud(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # Create collection
        res = auth_client.post(f'/api/workspaces/{ws_id}/collections')
        assert res.status_code == 201
        col = res.get_json()
        col_id = col['id']

        # Verify activity logged
        res_act = auth_client.get(f'/api/workspaces/{ws_id}/activities')
        data = res_act.get_json()
        create_event = next((x for x in data if x['event_category'] == 'collection' and x['action'] == 'create'), None)
        assert create_event is not None
        assert create_event['target_name'] == 'New Collection'
        assert create_event['target_id'] == col_id

        # Rename collection
        res_rename = auth_client.patch(f'/api/collections/{col_id}', json={'name': 'Renamed Collection'})
        assert res_rename.status_code == 200

        # Verify activity rename logged with diffs
        res_act = auth_client.get(f'/api/workspaces/{ws_id}/activities')
        data = res_act.get_json()
        rename_event = next((x for x in data if x['event_category'] == 'collection' and x['action'] == 'rename'), None)
        assert rename_event is not None
        assert rename_event['before_state'] == {'name': 'New Collection'}
        assert rename_event['after_state'] == {'name': 'Renamed Collection'}

    def test_credentials_scrubbing_and_redaction(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # Create a request
        res_col = auth_client.post(f'/api/workspaces/{ws_id}/collections')
        col_id = res_col.get_json()['id']
        res_req = auth_client.post(f'/api/collections/{col_id}/requests')
        req_id = res_req.get_json()['id']

        # Save request with sensitive header, query param, auth, and JSON body
        payload = {
            'url': 'http://secure-api.com',
            'headers': [
                {'key': 'Authorization', 'value': 'Bearer mysecretjwt'},
                {'key': 'Content-Type', 'value': 'application/json'}
            ],
            'params': [
                {'key': 'api_key', 'value': 'super-secret-key-123'},
                {'key': 'normal_param', 'value': 'safe'}
            ],
            'auth': {
                'type': 'bearer',
                'token': 'secret-token-payload'
            },
            'body': {
                'username': 'normal_user',
                'password': 'my-clear-password'
            }
        }
        res_save = auth_client.patch(f'/api/requests/{req_id}', json=payload)
        assert res_save.status_code == 200

        # Fetch activities to inspect log sanitization
        res_act = auth_client.get(f'/api/workspaces/{ws_id}/activities')
        data = res_act.get_json()
        update_event = next((x for x in data if x['event_category'] == 'request' and x['action'] == 'update'), None)
        
        assert update_event is not None
        after = update_event['after_state']
        
        # Verify Headers and Params scrubbed
        headers_list = after['headers']
        auth_header = next(h for h in headers_list if h['key'] == 'Authorization')
        assert auth_header['value'] == '[REDACTED]'
        normal_header = next(h for h in headers_list if h['key'] == 'Content-Type')
        assert normal_header['value'] == 'application/json'

        params_list = after['params']
        api_key_param = next(p for p in params_list if p['key'] == 'api_key')
        assert api_key_param['value'] == '[REDACTED]'
        normal_param = next(p for p in params_list if p['key'] == 'normal_param')
        assert normal_param['value'] == 'safe'

        # Verify Auth fields scrubbed
        assert after['auth']['token'] == '[REDACTED]'

        # Verify Body scrubbed
        assert after['body']['username'] == 'normal_user'
        assert after['body']['password'] == '[REDACTED]'

    def test_viewer_visibility_restrictions(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # 1. Workspace owner invites another user as 'viewer'
        other_user = signup_and_login(client, 'viewer_user', 'viewer@example.com')
        other_token = other_user['token']
        other_id = other_user['user_id']
        
        # Send invitation
        res_invite = auth_client.post(f'/api/workspaces/{ws_id}/invitations', 
                                      json={'username': 'viewer_user', 'role': 'viewer'})
        assert res_invite.status_code == 201
        inv_id = res_invite.get_json()['invitation_id']
        
        # Accept invitation
        res_accept = client.post(f'/api/invitations/{inv_id}/accept', 
                                 headers={'Authorization': f'Bearer {other_token}'})
        assert res_accept.status_code == 200

        # Owner renames workspace settings
        res_rename = auth_client.patch(f'/api/workspaces/{ws_id}', json={'name': 'Collaborative Space'})
        assert res_rename.status_code == 200

        # 2. Query activities as Owner -> Should see collaborator/workspace events
        res_owner = auth_client.get(f'/api/workspaces/{ws_id}/activities')
        owner_data = res_owner.get_json()
        
        invite_event = next((x for x in owner_data if x['event_category'] == 'membership' and x['action'] == 'invite'), None)
        rename_event = next((x for x in owner_data if x['event_category'] == 'workspace' and x['action'] == 'rename'), None)
        assert invite_event is not None
        assert rename_event is not None

        # 3. Query activities as Viewer -> Should NOT see membership or workspace events
        res_viewer = client.get(f'/api/workspaces/{ws_id}/activities', 
                                headers={'Authorization': f'Bearer {other_token}'})
        assert res_viewer.status_code == 200
        viewer_data = res_viewer.get_json()
        
        viewer_invite_event = next((x for x in viewer_data if x['event_category'] == 'membership'), None)
        viewer_rename_event = next((x for x in viewer_data if x['event_category'] == 'workspace'), None)
        assert viewer_invite_event is None
        assert viewer_rename_event is None
