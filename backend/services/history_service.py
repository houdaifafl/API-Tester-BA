from models.base import db
from models.history_model import History
from models.workspace_model import Workspace

def get_history_entries(workspace_id, user_id):
    """
    Retrieves up to 100 history entries for a given workspace in descending chronological order.
    Validates workspace existence and user ownership.
    """
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    if workspace.user_id != user_id:
        return None, 'forbidden'

    # Query latest 100 history items for this workspace
    entries = History.query.filter_by(workspace_id=workspace_id).order_by(History.id.desc()).limit(100).all()
    
    serialized = [
        {
            'id': e.id,
            'workspace_id': e.workspace_id,
            'method': e.method,
            'url': e.url,
            'params': e.params,
            'headers': e.headers,
            'body': e.body,
            'auth': e.auth,
            'created_at': (e.created_at.isoformat() + 'Z') if e.created_at else None
        }
        for e in entries
    ]
    return serialized, None

def create_history_entry(workspace_id, user_id, history_data):
    """
    Creates a new history entry for a given workspace.
    Validates workspace existence and user ownership.
    """
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    if workspace.user_id != user_id:
        return None, 'forbidden'

    method = history_data.get('method')
    url = history_data.get('url')
    if not method:
        return None, 'Method is required'
    if not url:
        return None, 'URL is required'

    new_entry = History(
        workspace_id=workspace_id,
        method=method,
        url=url,
        params=history_data.get('params'),
        headers=history_data.get('headers'),
        body=history_data.get('body'),
        auth=history_data.get('auth')
    )
    db.session.add(new_entry)
    db.session.commit()

    serialized = {
        'id': new_entry.id,
        'workspace_id': new_entry.workspace_id,
        'method': new_entry.method,
        'url': new_entry.url,
        'params': new_entry.params,
        'headers': new_entry.headers,
        'body': new_entry.body,
        'auth': new_entry.auth,
        'created_at': (new_entry.created_at.isoformat() + 'Z') if new_entry.created_at else None
    }
    return serialized, None
