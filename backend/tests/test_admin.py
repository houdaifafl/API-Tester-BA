from tests.conftest import signup_and_login
from models.base import db
from models.user_model import User
from models.audit_log_model import AdminAuditLog
from models.notification_model import UserNotification

class TestSuperAdmin:

    def _setup_admin(self, client):
        # Create normal user A
        user_a = signup_and_login(client, 'usera', 'usera@example.com')
        # Create normal user B
        user_b = signup_and_login(client, 'userb', 'userb@example.com')
        # Create admin user
        admin = signup_and_login(client, 'adminuser', 'admin@example.com')
        
        # Elevate admin in database
        u = db.session.get(User, admin['user_id'])
        u.is_admin = True
        db.session.commit()
        
        return {
            'user_a': user_a,
            'user_b': user_b,
            'admin': admin
        }

    def test_non_admin_cannot_access_endpoints(self, client):
        setup = self._setup_admin(client)
        user_a_token = setup['user_a']['token']
        
        # Try to list users
        res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {user_a_token}'})
        assert res.status_code == 403
        assert 'forbidden' in res.get_json()['error'].lower()

    def test_admin_can_list_users_and_workspaces(self, client):
        setup = self._setup_admin(client)
        admin_token = setup['admin']['token']
        
        # List users
        res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        users = res.get_json()
        assert len(users) >= 3
        usernames = [u['username'] for u in users]
        assert 'usera' in usernames
        assert 'adminuser' in usernames
        
        # List workspaces (admin workspaces are filtered out, so we only see User A and User B workspaces)
        res = client.get('/api/admin/workspaces', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        workspaces = res.get_json()
        assert len(workspaces) >= 2

    def test_admin_can_suspend_and_reactivate_user(self, client):
        setup = self._setup_admin(client)
        admin_token = setup['admin']['token']
        user_a_id = setup['user_a']['user_id']
        
        # Suspend User A
        res = client.post(f'/api/admin/users/{user_a_id}/suspend', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        
        # Verify User A cannot log in
        login_res = client.post('/api/auth/login', json={'username': 'usera', 'password': 'pass123'})
        assert login_res.status_code == 403
        assert 'suspended' in login_res.get_json()['error'].lower()
        
        # Reactivate User A
        res = client.post(f'/api/admin/users/{user_a_id}/reactivate', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        
        # Verify User A can log in now
        login_res2 = client.post('/api/auth/login', json={'username': 'usera', 'password': 'pass123'})
        assert login_res2.status_code == 200
        
        # Verify notifications were created
        notifications_res = client.get('/api/notifications', headers={'Authorization': f'Bearer {setup['user_a']['token']}'})
        assert notifications_res.status_code == 200
        notifs = notifications_res.get_json()
        assert len(notifs) == 2
        assert 'suspended' in notifs[1]['message'].lower()
        assert 're-activated' in notifs[0]['message'].lower()

    def test_admin_can_promote_and_demote_admin(self, client):
        setup = self._setup_admin(client)
        admin_token = setup['admin']['token']
        user_a_id = setup['user_a']['user_id']
        
        # Promote User A to admin
        res = client.post(f'/api/admin/users/{user_a_id}/promote', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        
        # Verify User A is now admin (should be able to list users)
        user_a_token = setup['user_a']['token']
        res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {user_a_token}'})
        assert res.status_code == 200
        
        # Demote User A from admin
        res = client.post(f'/api/admin/users/{user_a_id}/demote', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        
        # Verify User A is no longer admin
        res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {user_a_token}'})
        assert res.status_code == 403

    def test_admin_can_delete_user(self, client):
        setup = self._setup_admin(client)
        admin_token = setup['admin']['token']
        user_a_id = setup['user_a']['user_id']
        
        # Delete User A
        res = client.delete(f'/api/admin/users/{user_a_id}', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        
        # Verify User A is gone
        res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
        users = res.get_json()
        usernames = [u['username'] for u in users]
        assert 'usera' not in usernames

    def test_audit_logs_and_sensitive_logging(self, client):
        setup = self._setup_admin(client)
        admin_token = setup['admin']['token']
        
        # Trigger an action (suspend user b)
        user_b_id = setup['user_b']['user_id']
        client.post(f'/api/admin/users/{user_b_id}/suspend', headers={'Authorization': f'Bearer {admin_token}'})
        
        # Get audit logs
        res = client.get('/api/admin/audit-logs', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200
        logs = res.get_json()
        assert len(logs) >= 1
        assert logs[0]['action'] == 'suspend_user'
        
        # Log a sensitive view action
        client.post(f'/api/admin/workspaces/1/log-view', json={'details': 'Viewed Get data request details'}, headers={'Authorization': f'Bearer {admin_token}'})
        
        # Verify sensitive view logged
        res = client.get('/api/admin/audit-logs', headers={'Authorization': f'Bearer {admin_token}'})
        logs2 = res.get_json()
        assert logs2[0]['action'] == 'view_sensitive_data'
        assert 'Get data' in logs2[0]['target_snapshot']['details']
