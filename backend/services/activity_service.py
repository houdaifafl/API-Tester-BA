import re
from models.base import db
from models.activity_model import WorkspaceActivity
from models.workspace_member_model import WorkspaceMember
from models.workspace_model import Workspace

REDACT_PATTERN = re.compile(
    r'^(authorization|bearer|cookie|set-cookie|x-api-key|api[-_]key|apikey|token|access[-_]token)$', 
    re.IGNORECASE
)
REDACT_BODY_FIELDS = {'password', 'secret', 'token', 'password_hash'}

def _scrub_dict(data):
    if not isinstance(data, dict):
        return data
        
    # Check if this represents a key-value pair from list structures (e.g. headers or parameters)
    if 'key' in data and 'value' in data and data['key'] is not None:
        key_str = str(data['key']).strip()
        if REDACT_PATTERN.match(key_str) or key_str.lower() in REDACT_BODY_FIELDS:
            scrubbed = dict(data)
            scrubbed['value'] = "[REDACTED]"
            return scrubbed

    scrubbed = {}
    for k, v in data.items():
        if REDACT_PATTERN.match(k):
            scrubbed[k] = "[REDACTED]"
        elif isinstance(v, dict):
            scrubbed[k] = _scrub_dict(v)
        elif isinstance(v, list):
            scrubbed[k] = [_scrub_dict(item) if isinstance(item, dict) else item for item in v]
        elif k.lower() in REDACT_BODY_FIELDS:
            scrubbed[k] = "[REDACTED]"
        else:
            scrubbed[k] = v
    return scrubbed

def _scrub_state(state):
    if not state:
        return state
    # Create a deep copy using simple recursion/dict constructor to avoid modifying inputs
    if isinstance(state, dict):
        state_copy = dict(state)
        # Check if auth details are nested inside
        if 'auth' in state_copy and isinstance(state_copy['auth'], dict):
            state_copy['auth'] = _scrub_dict(state_copy['auth'])
        return _scrub_dict(state_copy)
    elif isinstance(state, list):
        return [_scrub_dict(item) if isinstance(item, dict) else item for item in state]
    return state

def log_activity(workspace_id, user_id, event_category, action, target_type, target_name, target_id=None, before_state=None, after_state=None):
    """
    Saves a chronological log of changes to the workspace_activities table.
    Scrubs sensitive credentials and tokens before saving.
    """
    scrubbed_before = _scrub_state(before_state)
    scrubbed_after = _scrub_state(after_state)

    # Limit string length of target_name
    if target_name and len(target_name) > 255:
        target_name = target_name[:252] + "..."

    log = WorkspaceActivity(
        workspace_id=workspace_id,
        user_id=user_id,
        event_category=event_category,
        action=action,
        target_type=target_type,
        target_name=target_name,
        target_id=target_id,
        before_state=scrubbed_before,
        after_state=scrubbed_after
    )
    db.session.add(log)
    # We flush/commit so that the log is written immediately in the transaction context
    # If the transaction is managed by the caller, the caller commits, but we ensure DB write
    db.session.flush()

def get_activities(workspace_id, user_id, limit=100, offset=0):
    """
    Retrieves chronological activity logs for the workspace, applying access control filters.
    """
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, 'workspace_not_found'

    # Check read access
    is_owner = (workspace.user_id == user_id)
    member_record = WorkspaceMember.query.filter_by(workspace_id=workspace_id, user_id=user_id).first()
    is_member = member_record is not None

    if not is_owner and not is_member:
        return None, 'forbidden'

    role = 'owner' if is_owner else (member_record.role or 'viewer')

    # Query builder
    query = WorkspaceActivity.query.filter_by(workspace_id=workspace_id)

    # Enforce role boundaries
    if role == 'viewer':
        # Viewers can only see: Collection modifications, Request modifications, Request executions
        query = query.filter(WorkspaceActivity.event_category.in_(['collection', 'request', 'execution']))

    logs = query.order_by(WorkspaceActivity.created_at.desc()).limit(limit).offset(offset).all()
    return [l.to_dict() for l in logs], None
