from tests.conftest import signup_and_login
from models.base import db
from models.workspace_member_model import WorkspaceMember
from models.invitation_model import Invitation

class TestSendInvitation:
    def test_send_invitation_success(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        signup_and_login(client, 'user_b', 'user_b@example.com')
        
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        assert res.status_code == 201
        data = res.get_json()
        assert 'invitation_id' in data
        assert data['message'] == 'Invitation sent successfully'

    def test_send_invitation_user_not_found(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'non_existent_user'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'User not found'

    def test_send_invitation_already_member(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'testuser'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'User is already a member'

    def test_send_invitation_already_pending(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        signup_and_login(client, 'user_b', 'user_b@example.com')
        
        res1 = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        assert res1.status_code == 201
        
        res2 = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        assert res2.status_code == 400
        assert res2.get_json()['error'] == 'Invitation already pending'

    def test_send_invitation_not_owner_or_member(self, client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        res = client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'testuser'}, headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_send_invitation_member_but_not_owner(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        # Invite user_b as editor and accept
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b', 'role': 'editor'})
        inv_id = invite_res.get_json()['invitation_id']
        client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        
        # Now user_b tries to invite testuser
        res = client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'testuser'}, headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_send_invitation_invalid_role(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'testuser', 'role': 'invalid_role'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invalid role specified'

    def test_send_invitation_workspace_not_found(self, auth_client):
        res = auth_client.post('/api/workspaces/9999/invitations', json={'username': 'testuser'})
        assert res.status_code == 404
        assert res.get_json()['error'] == 'Workspace not found'


class TestListPendingInvitations:
    def test_list_pending_invitations_success(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        
        res = client.get('/api/invitations/pending', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        invitations = res.get_json()
        assert len(invitations) == 1
        assert invitations[0]['workspace_id'] == ws_id
        assert invitations[0]['workspace_name'] == "Test's Space"
        assert invitations[0]['inviter_username'] == 'testuser'
        assert invitations[0]['status'] == 'pending'


class TestAcceptInvitation:
    def test_accept_invitation_success(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Invitation accepted'
        
        workspaces_res = client.get('/api/workspaces', headers={'Authorization': f'Bearer {other_token}'})
        ws_list = workspaces_res.get_json()
        ws_ids = [w['id'] for w in ws_list]
        assert ws_id in ws_ids
        
        cols_res = client.get(f'/api/workspaces/{ws_id}/collections', headers={'Authorization': f'Bearer {other_token}'})
        assert cols_res.status_code == 200
        
        history_post_res = client.post(f'/api/workspaces/{ws_id}/history', json={
            'method': 'GET',
            'url': 'http://example.com'
        }, headers={'Authorization': f'Bearer {other_token}'})
        assert history_post_res.status_code == 201
        
        history_get_res = client.get(f'/api/workspaces/{ws_id}/history', headers={'Authorization': f'Bearer {other_token}'})
        assert history_get_res.status_code == 200
        assert len(history_get_res.get_json()) == 1

    def test_accept_invitation_not_pending(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        
        res = client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invitation is not pending'

    def test_accept_invitation_forbidden(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        signup_and_login(client, 'user_b', 'user_b@example.com')
        
        user_c = signup_and_login(client, 'user_c', 'user_c@example.com')
        c_token = user_c['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {c_token}'})
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_accept_invitation_not_found(self, auth_client):
        res = auth_client.post('/api/invitations/9999/accept')
        assert res.status_code == 404

    def test_accept_invitation_as_viewer(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b', 'role': 'viewer'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        
        # Verify role in membership is 'viewer'
        with client.application.app_context():
            member = WorkspaceMember.query.filter_by(workspace_id=ws_id, user_id=other_user['user_id']).first()
            assert member is not None
            assert member.role == 'viewer'

    def test_accept_invitation_as_editor(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b', 'role': 'editor'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/accept', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        
        # Verify role in membership is 'editor'
        with client.application.app_context():
            member = WorkspaceMember.query.filter_by(workspace_id=ws_id, user_id=other_user['user_id']).first()
            assert member is not None
            assert member.role == 'editor'


class TestDeclineInvitation:
    def test_decline_invitation_success(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/decline', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 200
        assert res.get_json()['message'] == 'Invitation declined'
        
        workspaces_res = client.get('/api/workspaces', headers={'Authorization': f'Bearer {other_token}'})
        ws_list = workspaces_res.get_json()
        ws_ids = [w['id'] for w in ws_list]
        assert ws_id not in ws_ids

    def test_decline_invitation_not_pending(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        other_user = signup_and_login(client, 'user_b', 'user_b@example.com')
        other_token = other_user['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        client.post(f'/api/invitations/{inv_id}/decline', headers={'Authorization': f'Bearer {other_token}'})
        
        res = client.post(f'/api/invitations/{inv_id}/decline', headers={'Authorization': f'Bearer {other_token}'})
        assert res.status_code == 400
        assert res.get_json()['error'] == 'Invitation is not pending'

    def test_decline_invitation_forbidden(self, client, auth_client, auth_data):
        create_res = auth_client.post('/api/workspaces', json={'name': 'A Shared Space'})
        ws_id = create_res.get_json()['id']
        
        signup_and_login(client, 'user_b', 'user_b@example.com')
        
        user_c = signup_and_login(client, 'user_c', 'user_c@example.com')
        c_token = user_c['token']
        
        invite_res = auth_client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'user_b'})
        inv_id = invite_res.get_json()['invitation_id']
        
        res = client.post(f'/api/invitations/{inv_id}/decline', headers={'Authorization': f'Bearer {c_token}'})
        assert res.status_code == 403
        assert res.get_json()['error'] == 'Forbidden'

    def test_decline_invitation_not_found(self, auth_client):
        res = auth_client.post('/api/invitations/9999/decline')
        assert res.status_code == 404
