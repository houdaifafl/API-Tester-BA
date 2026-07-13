import pytest
from models.base import db
from models.user_model import User
from models.audit_log_model import AdminAuditLog
from services.jwt_service import encode_token

class TestAuditLogForensics:

    def test_audit_logs_retained_on_admin_deletion(self, client):
        # Create an Admin User
        client.post('/api/auth/signup', json={
            'username': 'admin_forensic_test',
            'first_name': 'Admin',
            'email': 'admin_forensic@example.com',
            'password': 'password123'
        })
        
        # Manually promote to Admin in database
        with client.application.app_context():
            admin_user = User.query.filter_by(username='admin_forensic_test').first()
            assert admin_user is not None
            admin_user.is_admin = True
            db.session.commit()
            admin_id = admin_user.id

        # Log in to get token
        login_res = client.post('/api/auth/login', json={
            'username': 'admin_forensic_test',
            'password': 'password123'
        })
        admin_token = login_res.get_json()['token']

        # Setup another user to target for admin action (e.g. suspend)
        client.post('/api/auth/signup', json={
            'username': 'victim_user',
            'first_name': 'Victim',
            'email': 'victim@example.com',
            'password': 'password123'
        })
        with client.application.app_context():
            victim = User.query.filter_by(username='victim_user').first()
            victim_id = victim.id

        # Admin suspends victim user (creating audit log)
        res = client.post(f'/api/admin/users/{victim_id}/suspend', headers={'Authorization': f'Bearer {admin_token}'})
        assert res.status_code == 200

        # Verify audit log was created
        with client.application.app_context():
            logs = AdminAuditLog.query.filter_by(admin_id=admin_id).all()
            assert len(logs) == 1
            assert logs[0].admin_username == 'admin_forensic_test'
            log_id = logs[0].id

        # Delete the admin user (need another admin to delete them)
        # Create a second admin to perform deletion
        client.post('/api/auth/signup', json={
            'username': 'super_admin',
            'first_name': 'Super',
            'email': 'super@example.com',
            'password': 'password123'
        })
        with client.application.app_context():
            super_user = User.query.filter_by(username='super_admin').first()
            super_user.is_admin = True
            db.session.commit()

        super_login = client.post('/api/auth/login', json={
            'username': 'super_admin',
            'password': 'password123'
        })
        super_token = super_login.get_json()['token']

        # Delete the first admin
        del_res = client.delete(f'/api/admin/users/{admin_id}', headers={'Authorization': f'Bearer {super_token}'})
        assert del_res.status_code == 200

        # Verify the admin user is deleted
        with client.application.app_context():
            deleted_admin = db.session.get(User, admin_id)
            assert deleted_admin is None

        # Verify the audit log STILL EXISTS (Retained)
        with client.application.app_context():
            retained_log = db.session.get(AdminAuditLog, log_id)
            assert retained_log is not None
            # admin_id is set to None due to SET NULL
            assert retained_log.admin_id is None
            # admin_username is retained
            assert retained_log.admin_username == 'admin_forensic_test'

        # Verify that fetching audit logs returns the log with 'admin_forensic_test' as username
        logs_res = client.get('/api/admin/audit-logs', headers={'Authorization': f'Bearer {super_token}'})
        assert logs_res.status_code == 200
        api_logs = logs_res.get_json()
        matching_log = [l for l in api_logs if l['id'] == log_id][0]
        assert matching_log['admin_id'] is None
        assert matching_log['admin_username'] == 'admin_forensic_test'
