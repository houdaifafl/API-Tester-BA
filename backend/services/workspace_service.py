from models.workspace_model import Workspace
from models.base import db

def get_user_workspaces(user_id):
    workspaces = Workspace.query.filter_by(user_id=user_id).all()
    return [{'id': w.id, 'name': w.name} for w in workspaces]

def create_workspace(user_id, name):
    workspace = Workspace(name=name, user_id=user_id)
    db.session.add(workspace)
    db.session.commit()
    return {'id': workspace.id, 'name': workspace.name}
