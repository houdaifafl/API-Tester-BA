from models.workspace_model import Workspace
from models.workspace_member_model import WorkspaceMember
from models.user_model import User
from models.invitation_model import Invitation
from models.base import db
from services.collection_service import ensure_default_collection
from services.activity_service import log_activity

def get_user_workspaces(user_id):
    # Owned workspaces
    owned_workspaces = Workspace.query.filter_by(user_id=user_id).all()
    # Workspaces where user is a member
    memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()
    member_workspaces = [m.workspace for m in memberships if m.workspace]
    
    all_workspaces = []
    seen_ids = set()
    for w in owned_workspaces + member_workspaces:
        if w.id not in seen_ids:
            seen_ids.add(w.id)
            all_workspaces.append(w)
            
    return [{'id': w.id, 'name': w.name, 'is_default': w.is_default, 'is_owner': w.user_id == user_id} for w in all_workspaces]

def create_workspace(user_id, name, is_default=False):
    workspace = Workspace(name=name, user_id=user_id, is_default=is_default)
    db.session.add(workspace)
    db.session.flush()  # obtain workspace.id before seeding the default collection
    ensure_default_collection(workspace.id)  # creates collection + default requests and commits
    log_activity(workspace.id, user_id, 'workspace', 'create', 'settings', name, workspace.id)
    db.session.commit()
    return {'id': workspace.id, 'name': workspace.name, 'is_default': workspace.is_default, 'is_owner': True}

def get_workspace_by_id(workspace_id, user_id):
    workspace = Workspace.query.filter_by(id=workspace_id).first()
    if not workspace:
        return None, 'not_found'
    
    is_owner = (workspace.user_id == user_id)
    is_member = False
    role = 'viewer'
    if is_owner:
        role = 'owner'
    else:
        member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
        is_member = member_record is not None
        if is_member:
            role = member_record.role or 'viewer'

    if not is_owner and not is_member:
        return None, 'forbidden'
        
    return {'id': workspace.id, 'name': workspace.name, 'is_default': workspace.is_default, 'role': role}, None

def delete_workspace(workspace_id, user_id):
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return None, 'Workspace not found'
    if workspace.is_default:
        return None, 'Cannot delete the default workspace'
    log_activity(workspace_id, user_id, 'workspace', 'delete', 'settings', workspace.name, workspace_id)
    db.session.delete(workspace)
    db.session.commit()
    return True, None

def check_user_write_access(workspace_id, user_id):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return False, 'Workspace not found'
        
    is_owner = (workspace.user_id == user_id)
    if is_owner:
        return True, None
        
    member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
    if not member:
        return False, 'Forbidden'
        
    if member.role == 'editor':
        return True, None
        
    return False, 'Forbidden'

def leave_workspace(workspace_id, user_id):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'Workspace not found'
    if workspace.user_id == user_id:
        return None, 'Owners cannot leave their own workspace'
    member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
    if not member:
        return None, 'Membership not found'
    username = member.user.username if member.user else 'Unknown'
    log_activity(workspace_id, user_id, 'membership', 'leave', 'member', username, user_id)
    db.session.delete(member)
    db.session.commit()
    return True, None

def check_user_read_access(workspace_id, user_id):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return False, 'Workspace not found'
        
    is_owner = (workspace.user_id == user_id)
    if is_owner:
        return True, None
        
    member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
    if member:
        return True, None
        
    return False, 'Forbidden'


def update_workspace_name(workspace_id, user_id, name):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    if workspace.user_id != user_id:
        return None, 'forbidden'
        
    old_name = workspace.name
    workspace.name = name
    log_activity(workspace_id, user_id, 'workspace', 'rename', 'settings', name, workspace_id,
                 before_state={'name': old_name}, after_state={'name': name})
    db.session.commit()
    return True, None

def update_member_role(workspace_id, user_id, target_user_id, role):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    if workspace.user_id != user_id:
        return None, 'forbidden'
        
    member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=target_user_id).first()
    if not member:
        return None, 'membership_not_found'
        
    old_role = member.role or 'viewer'
    member.role = role
    target_user = db.session.get(User, target_user_id)
    username = target_user.username if target_user else 'Unknown'
    log_activity(workspace_id, user_id, 'membership', 'role_change', 'member', username, target_user_id,
                 before_state={'role': old_role}, after_state={'role': role})
    db.session.commit()
    return True, None

def remove_member(workspace_id, user_id, target_user_id):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    if workspace.user_id != user_id:
        return None, 'forbidden'
        
    member = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=target_user_id).first()
    if not member:
        return None, 'membership_not_found'
        
    target_user = db.session.get(User, target_user_id)
    username = target_user.username if target_user else 'Unknown'
    log_activity(workspace_id, user_id, 'membership', 'leave', 'member', username, target_user_id)
    db.session.delete(member)
    db.session.commit()
    return True, None

def get_workspace_collaborators(workspace_id, user_id):
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    is_owner = (workspace.user_id == user_id)
    member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
    if not is_owner and not member_record:
        return None, 'forbidden'
        
    memberships = WorkspaceMember.query.filter_by(workspace_id=workspace_id).all()
    serialized_members = []
    for m in memberships:
        serialized_members.append({
            'user_id': m.user_id,
            'username': m.user.username if m.user else 'Unknown',
            'email': m.user.email if m.user else 'Unknown',
            'role': m.role or 'viewer'
        })
        
    invitations = Invitation.query.filter_by(workspace_id=workspace_id, status='pending').all()
    serialized_invitations = []
    for inv in invitations:
        serialized_invitations.append({
            'id': inv.id,
            'username': inv.invitee.username if inv.invitee else 'Unknown',
            'email': inv.invitee.email if inv.invitee else 'Unknown',
            'role': inv.role or 'viewer'
        })
        
    return {
        'members': serialized_members,
        'invitations': serialized_invitations
    }, None

