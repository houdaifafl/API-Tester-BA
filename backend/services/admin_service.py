from models.base import db
from models.user_model import User
from models.workspace_model import Workspace
from models.collection_model import Collection
from models.audit_log_model import AdminAuditLog
from models.notification_model import UserNotification
from sqlalchemy import select

def _write_audit_log(admin_id, action, target_type, target_id, target_snapshot=None):
    log = AdminAuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        target_snapshot=target_snapshot
    )
    db.session.add(log)
    db.session.flush()

def verify_admin_status(user_id):
    user = db.session.get(User, user_id)
    return user is not None and user.is_admin

def get_all_users(admin_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    users = User.query.all()
    res = []
    for u in users:
        # Avoid including passwords
        res.append({
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'email': u.email,
            'is_admin': u.is_admin,
            'is_suspended': u.is_suspended,
            'workspaces_count': len(u.workspaces)
        })
    return res, None

def suspend_user(admin_id, target_user_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    user = db.session.get(User, target_user_id)
    if not user:
        return None, 'User not found'
    if user.id == admin_id:
        return None, 'You cannot suspend yourself'
    user.is_suspended = True
    
    # Write audit log
    _write_audit_log(admin_id, 'suspend_user', 'user', user.id, {'username': user.username})
    
    # Create notification
    notif = UserNotification(user_id=user.id, message='Your account has been suspended by an administrator.')
    db.session.add(notif)
    
    db.session.commit()
    return True, None

def reactivate_user(admin_id, target_user_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    user = db.session.get(User, target_user_id)
    if not user:
        return None, 'User not found'
    user.is_suspended = False
    
    # Write audit log
    _write_audit_log(admin_id, 'reactivate_user', 'user', user.id, {'username': user.username})
    
    # Create notification
    notif = UserNotification(user_id=user.id, message='Your account has been re-activated. You can log in again.')
    db.session.add(notif)
    
    db.session.commit()
    return True, None

def delete_user(admin_id, target_user_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    user = db.session.get(User, target_user_id)
    if not user:
        return None, 'User not found'
    if user.id == admin_id:
        return None, 'You cannot delete yourself'
    
    snapshot = {'username': user.username, 'email': user.email}
    _write_audit_log(admin_id, 'delete_user', 'user', user.id, snapshot)
    
    db.session.delete(user)
    db.session.commit()
    return True, None

def promote_to_admin(admin_id, target_user_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    user = db.session.get(User, target_user_id)
    if not user:
        return None, 'User not found'
    # Delete all workspaces owned by the promoted user, since admins do not use workspaces
    for ws in list(user.workspaces):
      db.session.delete(ws)

    user.is_admin = True
    
    _write_audit_log(admin_id, 'promote_admin', 'user', user.id, {'username': user.username})
    db.session.commit()
    return True, None

def demote_from_admin(admin_id, target_user_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    user = db.session.get(User, target_user_id)
    if not user:
        return None, 'User not found'
    if user.id == admin_id:
        return None, 'You cannot demote yourself'
    user.is_admin = False
    
    _write_audit_log(admin_id, 'demote_admin', 'user', user.id, {'username': user.username})
    db.session.commit()
    return True, None

def get_all_workspaces(admin_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    workspaces = Workspace.query.all()
    res = []
    for w in workspaces:
        # Exclude workspaces owned by admins
        if w.owner and w.owner.is_admin:
            continue
        res.append({
            'id': w.id,
            'name': w.name,
            'is_default': w.is_default,
            'owner_username': w.owner.username if w.owner else 'Unknown',
            'collections_count': len(w.collections),
            'members_count': len(w.memberships) + 1
        })
    return res, None

def delete_workspace_by_admin(admin_id, workspace_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    ws = db.session.get(Workspace, workspace_id)
    if not ws:
        return None, 'Workspace not found'
    
    _write_audit_log(admin_id, 'delete_workspace', 'workspace', ws.id, {'name': ws.name})
    db.session.delete(ws)
    db.session.commit()
    return True, None

def get_workspace_collections(admin_id, workspace_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    ws = db.session.get(Workspace, workspace_id)
    if not ws:
        return None, 'Workspace not found'
        
    res = []
    for col in ws.collections:
        requests = []
        for req in col.requests:
            requests.append({
                'id': req.id,
                'name': req.name,
                'method': req.method,
                'url': req.url,
                'params': req.params,
                'headers': req.headers,
                'body': req.body,
                'auth': req.auth
            })
        res.append({
            'id': col.id,
            'name': col.name,
            'is_default': col.is_default,
            'requests': requests
        })
    return res, None

def delete_collection_by_admin(admin_id, collection_id):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    col = db.session.get(Collection, collection_id)
    if not col:
        return None, 'Collection not found'
        
    _write_audit_log(admin_id, 'delete_collection', 'collection', col.id, {'name': col.name, 'workspace_id': col.workspace_id})
    db.session.delete(col)
    db.session.commit()
    return True, None

def log_sensitive_view(admin_id, workspace_id, details):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    _write_audit_log(admin_id, 'view_sensitive_data', 'workspace', workspace_id, {'details': details})
    db.session.commit()
    return True, None

def get_audit_logs(admin_id, limit=100, offset=0):
    if not verify_admin_status(admin_id):
        return None, 'Forbidden'
    logs = AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc()).limit(limit).offset(offset).all()
    return [l.to_dict() for l in logs], None

def get_user_notifications(user_id):
    notifs = UserNotification.query.filter_by(user_id=user_id).order_by(UserNotification.created_at.desc()).all()
    return [n.to_dict() for n in notifs], None

def mark_notifications_read(user_id):
    notifs = UserNotification.query.filter_by(user_id=user_id, is_read=False).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return True, None
