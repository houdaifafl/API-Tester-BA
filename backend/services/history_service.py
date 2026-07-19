from models.base import db
from models.history_model import History
from models.workspace_model import Workspace
from models.workspace_member_model import WorkspaceMember
from services.encryption_service import (
    mask_sensitive_headers, mask_sensitive_auth, should_mask_response_data
)
from services.activity_service import log_activity

def get_history_entries(workspace_id, user_id):
    """
    Retrieves up to 100 history entries for a given workspace in descending chronological order.
    Validates workspace existence and user ownership/membership.
    """
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    
    is_owner = (workspace.user_id == user_id)
    is_member = False
    if not is_owner:
        member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
        is_member = member_record is not None

    if not is_owner and not is_member:
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
            'headers': mask_sensitive_headers(e.headers),
            'body': e.body,
            'auth': mask_sensitive_auth(e.auth),
            'status': e.status,
            'response_time': e.response_time,
            'data': e.data,
            'created_at': (e.created_at.isoformat() + 'Z') if e.created_at else None
        }
        for e in entries
    ]
    return serialized, None

def create_history_entry(workspace_id, user_id, history_data):
    """
    Creates a new history entry for a given workspace.
    Validates workspace existence and user ownership/membership.
    """
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'not_found'
    
    is_owner = (workspace.user_id == user_id)
    is_member = False
    if not is_owner:
        member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
        is_member = member_record is not None

    if not is_owner and not is_member:
        return None, 'forbidden'

    method = history_data.get('method')
    url = history_data.get('url')
    if not method:
        return None, 'Method is required'
    if not url:
        return None, 'URL is required'

    resp_data = history_data.get('data')
    if should_mask_response_data(history_data):
        resp_data = {'message': 'Response body not stored due to security policy (contains sensitive request/response data)'}

    status = history_data.get('status')
    response_time = history_data.get('response_time')

    new_entry = History(
        workspace_id=workspace_id,
        method=method,
        url=url,
        params=history_data.get('params'),
        headers=history_data.get('headers'),
        body=history_data.get('body'),
        auth=history_data.get('auth'),
        status=status,
        response_time=response_time,
        data=resp_data
    )
    db.session.add(new_entry)
    
    # Calculate response time in ms for activity feed log
    resp_time_ms = int(response_time * 1000) if response_time is not None else 0
    log_activity(
        workspace_id,
        user_id,
        'execution',
        'execute',
        'request',
        f"{method} {url}",
        before_state=None,
        after_state={"status_code": status, "response_time_ms": resp_time_ms}
    )
    
    db.session.commit()

    serialized = {
        'id': new_entry.id,
        'workspace_id': new_entry.workspace_id,
        'method': new_entry.method,
        'url': new_entry.url,
        'params': new_entry.params,
        'headers': mask_sensitive_headers(new_entry.headers),
        'body': new_entry.body,
        'auth': mask_sensitive_auth(new_entry.auth),
        'status': new_entry.status,
        'response_time': new_entry.response_time,
        'data': new_entry.data,
        'created_at': (new_entry.created_at.isoformat() + 'Z') if new_entry.created_at else None
    }
    return serialized, None
