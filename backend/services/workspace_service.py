from models.workspace_model import Workspace
from models.workspace_member_model import WorkspaceMember
from models.base import db
from services.collection_service import ensure_default_collection

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
    db.session.delete(member)
    db.session.commit()
    return True, None
