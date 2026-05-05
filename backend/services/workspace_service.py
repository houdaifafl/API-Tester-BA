from models.workspace_model import Workspace
from models.base import db
from services.collection_service import ensure_default_collection

def get_user_workspaces(user_id):
    workspaces = Workspace.query.filter_by(user_id=user_id).all()
    return [{'id': w.id, 'name': w.name, 'is_default': w.is_default} for w in workspaces]

def create_workspace(user_id, name):
    workspace = Workspace(name=name, user_id=user_id)
    db.session.add(workspace)
    db.session.flush()  # obtain workspace.id before seeding the default collection
    ensure_default_collection(workspace.id)  # creates collection + default requests and commits
    return {'id': workspace.id, 'name': workspace.name, 'is_default': workspace.is_default}

def delete_workspace(workspace_id, user_id):
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first()
    if not workspace:
        return None, 'Workspace not found'
    if workspace.is_default:
        return None, 'Cannot delete the default workspace'
    db.session.delete(workspace)
    db.session.commit()
    return True, None
