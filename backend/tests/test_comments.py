import pytest
from tests.conftest import signup_and_login
from models.comment_model import Comment
from models.workspace_member_model import WorkspaceMember
from models.base import db

class TestCommentsApi:

    def _create_workspace(self, auth_client, name):
        res = auth_client.post('/api/workspaces', json={'name': name})
        assert res.status_code == 201
        return res.get_json()['id']

    def _create_comment(self, auth_client, ws_id, content, parent_id=None, request_id=None, target_tab=None, target_key=None, headers=None):
        payload = {'content': content}
        if parent_id is not None:
            payload['parent_id'] = parent_id
        if request_id is not None:
            payload['request_id'] = request_id
        if target_tab is not None:
            payload['target_tab'] = target_tab
        if target_key is not None:
            payload['target_key'] = target_key
        
        kwargs = {'json': payload}
        if headers is not None:
            kwargs['headers'] = headers
            
        res = auth_client.post(f'/api/workspaces/{ws_id}/comments', **kwargs)
        return res

    def test_list_comments_empty_initially(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = auth_client.get(f'/api/workspaces/{ws_id}/comments')
        assert res.status_code == 200
        assert res.get_json() == []

    def test_create_and_get_comment(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        res = self._create_comment(auth_client, ws_id, "Hello workspace!")
        assert res.status_code == 201
        data = res.get_json()
        assert data['content'] == "Hello workspace!"
        assert data['username'] == "testuser"
        assert data['parent_id'] is None
        assert data['replies'] == []

        # List comments
        res_list = auth_client.get(f'/api/workspaces/{ws_id}/comments')
        assert res_list.status_code == 200
        comments = res_list.get_json()
        assert len(comments) == 1
        assert comments[0]['id'] == data['id']
        assert comments[0]['content'] == "Hello workspace!"

    def test_single_level_nested_replies(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        # Create parent comment
        p_res = self._create_comment(auth_client, ws_id, "Parent comment")
        assert p_res.status_code == 201
        parent_id = p_res.get_json()['id']

        # Reply to parent comment
        r_res = self._create_comment(auth_client, ws_id, "Reply comment", parent_id=parent_id)
        assert r_res.status_code == 201
        reply_data = r_res.get_json()
        assert reply_data['parent_id'] == parent_id

        # Verify nesting in list comments
        list_res = auth_client.get(f'/api/workspaces/{ws_id}/comments')
        comments = list_res.get_json()
        assert len(comments) == 1
        assert comments[0]['id'] == parent_id
        assert len(comments[0]['replies']) == 1
        assert comments[0]['replies'][0]['id'] == reply_data['id']
        assert comments[0]['replies'][0]['content'] == "Reply comment"

    def test_infinite_nesting_is_blocked(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        # Parent
        p_id = self._create_comment(auth_client, ws_id, "Parent").get_json()['id']
        # Child
        c_id = self._create_comment(auth_client, ws_id, "Child", parent_id=p_id).get_json()['id']
        # Grandchild (should be blocked)
        gc_res = self._create_comment(auth_client, ws_id, "Grandchild", parent_id=c_id)
        assert gc_res.status_code == 400
        assert "Nested child comments are not allowed" in gc_res.get_json()['error']

    def test_comments_in_forbidden_workspace_are_blocked(self, client, auth_client, auth_data):
        # Create workspace for another user
        other = signup_and_login(client, 'otheruser', 'other@example.com')
        other_token = other['token']
        res_ws = client.post('/api/workspaces', json={'name': 'Private Workspace'}, headers={'Authorization': f'Bearer {other_token}'})
        other_ws_id = res_ws.get_json()['id']

        # Try to view comments as main user
        res_list = auth_client.get(f'/api/workspaces/{other_ws_id}/comments')
        assert res_list.status_code == 403

        # Try to post comments as main user
        res_post = self._create_comment(auth_client, other_ws_id, "Spamming")
        assert res_post.status_code == 403

    def test_edit_own_comment(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        c_id = self._create_comment(auth_client, ws_id, "Original content").get_json()['id']

        res_edit = auth_client.patch(f'/api/comments/{c_id}', json={'content': 'Updated content'})
        assert res_edit.status_code == 200
        assert res_edit.get_json()['content'] == "Updated content"

        # Verify in DB list
        res_list = auth_client.get(f'/api/workspaces/{ws_id}/comments')
        assert res_list.get_json()[0]['content'] == "Updated content"

    def test_edit_others_comment_is_blocked(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        # Create comment as owner
        c_id = self._create_comment(auth_client, ws_id, "Owner comment").get_json()['id']

        # Login other user
        other = signup_and_login(client, 'othereditor', 'othered@example.com')
        other_token = other['token']
        other_headers = {'Authorization': f'Bearer {other_token}'}

        # Join workspace as editor
        client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'othereditor', 'role': 'editor'}, headers=auth_client.headers)
        invs = client.get('/api/invitations/pending', headers=other_headers).get_json()
        client.post(f'/api/invitations/{invs[0]["id"]}/accept', headers=other_headers)

        # Attempt to edit as other user
        res_edit = client.patch(f'/api/comments/{c_id}', json={'content': 'Hacked'}, headers=other_headers)
        assert res_edit.status_code == 403

    def test_delete_permissions(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        
        # Invite another user to workspace
        other = signup_and_login(client, 'member', 'member@example.com')
        other_token = other['token']
        other_headers = {'Authorization': f'Bearer {other_token}'}

        client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'member', 'role': 'viewer'}, headers=auth_client.headers)
        invs = client.get('/api/invitations/pending', headers=other_headers).get_json()
        client.post(f'/api/invitations/{invs[0]["id"]}/accept', headers=other_headers)

        # Post comment as workspace member
        m_c_id = self._create_comment(client, ws_id, "Member comment", headers=other_headers).get_json()['id']

        # Post comment as workspace owner
        o_c_id = self._create_comment(auth_client, ws_id, "Owner comment").get_json()['id']

        # 1. Member can delete their own comment
        res_del_own = client.delete(f'/api/comments/{m_c_id}', headers=other_headers)
        assert res_del_own.status_code == 200

        # 2. Member CANNOT delete owner's comment
        res_del_other = client.delete(f'/api/comments/{o_c_id}', headers=other_headers)
        assert res_del_other.status_code == 403

        # Re-post member comment
        m_c_id_new = self._create_comment(client, ws_id, "Member comment 2", headers=other_headers).get_json()['id']

        # 3. Owner can delete member's comment
        res_owner_del = auth_client.delete(f'/api/comments/{m_c_id_new}')
        assert res_owner_del.status_code == 200

    def test_param_key_rename_cascade(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        req_id = cols[0]['requests'][0]['id']

        # Save request with a parameter
        row_id = 12345.67
        params = [{'id': row_id, 'key': 'limit', 'value': '10', 'description': ''}]
        auth_client.patch(f'/api/requests/{req_id}', json={'params': params})

        # Add comment bound to parameter
        c_res = self._create_comment(auth_client, ws_id, "Annotating limit key", request_id=req_id, target_tab='params', target_key='limit')
        assert c_res.status_code == 201
        c_id = c_res.get_json()['id']

        # Rename the parameter key
        new_params = [{'id': row_id, 'key': 'pageSize', 'value': '10', 'description': ''}]
        save_res = auth_client.patch(f'/api/requests/{req_id}', json={'params': new_params})
        assert save_res.status_code == 200

        # Verify comment target_key was renamed
        comments = auth_client.get(f'/api/workspaces/{ws_id}/comments').get_json()
        assert comments[0]['id'] == c_id
        assert comments[0]['target_key'] == 'pageSize'

    def test_request_cascade_delete(self, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']
        cols = auth_client.get(f'/api/workspaces/{ws_id}/collections').get_json()
        req_id = cols[0]['requests'][0]['id']

        # Create comment bound to request
        c_id = self._create_comment(auth_client, ws_id, "Bound to request", request_id=req_id).get_json()['id']

        # Delete the request
        del_res = auth_client.delete(f'/api/requests/{req_id}')
        assert del_res.status_code == 200

        # Verify comment is deleted from DB
        comments = auth_client.get(f'/api/workspaces/{ws_id}/comments').get_json()
        assert len(comments) == 0

    def test_deactivated_user(self, client, auth_client, auth_data):
        ws_id = auth_data['default_workspace_id']

        # Invite another user
        other = signup_and_login(client, 'exmember', 'ex@example.com')
        other_token = other['token']
        other_headers = {'Authorization': f'Bearer {other_token}'}

        client.post(f'/api/workspaces/{ws_id}/invitations', json={'username': 'exmember', 'role': 'viewer'}, headers=auth_client.headers)
        invs = client.get('/api/invitations/pending', headers=other_headers).get_json()
        client.post(f'/api/invitations/{invs[0]["id"]}/accept', headers=other_headers)

        # Comment as other user
        self._create_comment(client, ws_id, "Valuable feedback", headers=other_headers)

        # Remove user from workspace
        # Wait, how does a user leave workspace? Route: DELETE /api/workspaces/<workspace_id>/leave
        leave_res = client.delete(f'/api/workspaces/{ws_id}/leave', headers=other_headers)
        assert leave_res.status_code == 200

        # Retrieve comments as owner, verify comment creator is "Deactivated User"
        comments = auth_client.get(f'/api/workspaces/{ws_id}/comments').get_json()
        assert len(comments) == 1
        assert comments[0]['username'] == "Deactivated User"
