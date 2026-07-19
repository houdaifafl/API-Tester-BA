from models.request_model import Request
from models.collection_model import Collection
from models.base import db
from services.activity_service import log_activity


def create_request(collection_id, user_id):
    collection = db.session.get(Collection, collection_id)
    if not collection:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(collection.workspace_id, user_id)
    if not allowed:
        return None, err

    new_request = Request(
        name='New Request',
        method='GET',
        url='',
        params=None,
        headers=None,
        body=None,
        collection_id=collection_id,
    )
    db.session.add(new_request)
    db.session.flush()
    log_activity(collection.workspace_id, user_id, 'request', 'create', 'request', 'New Request', new_request.id)
    db.session.commit()

    return {
        'id': new_request.id,
        'name': new_request.name,
        'method': new_request.method,
        'url': new_request.url,
        'collection_id': new_request.collection_id,
    }, None


def rename_request(request_id, new_name, user_id):
    req = db.session.get(Request, request_id)
    if not req:
        return None, 'Request not found'

    collection = db.session.get(Collection, req.collection_id) if req.collection_id else None
    if not collection:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(collection.workspace_id, user_id)
    if not allowed:
        return None, err

    old_name = req.name
    req.name = new_name
    log_activity(collection.workspace_id, user_id, 'request', 'rename', 'request', new_name, req.id,
                 before_state={'name': old_name}, after_state={'name': new_name})
    db.session.commit()
    return {'id': req.id, 'name': req.name}, None


_VALID_METHODS = {'GET', 'POST', 'PUT', 'DELETE'}

def update_request_method(request_id, method, user_id):
    if method not in _VALID_METHODS:
        return None, 'Invalid method'
    req = db.session.get(Request, request_id)
    if not req:
        return None, 'Request not found'

    collection = db.session.get(Collection, req.collection_id) if req.collection_id else None
    if not collection:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(collection.workspace_id, user_id)
    if not allowed:
        return None, err

    old_method = req.method
    req.method = method
    log_activity(collection.workspace_id, user_id, 'request', 'update', 'request', req.name, req.id,
                 before_state={'method': old_method}, after_state={'method': method})
    db.session.commit()
    return {'id': req.id, 'method': req.method}, None


def save_request(request_id, data, user_id):
    req = db.session.get(Request, request_id)
    if not req:
        return None, 'Request not found'

    collection = db.session.get(Collection, req.collection_id) if req.collection_id else None
    if not collection:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(collection.workspace_id, user_id)
    if not allowed:
        return None, err

    from models.comment_model import Comment

    # Check for parameter key renames
    if 'params' in data:
        old_params = req.params or []
        new_params = data['params'] or []
        old_map = {p['id']: p['key'].strip() for p in old_params if 'id' in p and p.get('key')}
        for p in new_params:
            if 'id' in p and p.get('key'):
                new_key = p['key'].strip()
                pid = p['id']
                if pid in old_map:
                    old_key = old_map[pid]
                    if old_key != new_key and new_key:
                        Comment.query.filter_by(
                            request_id=req.id,
                            target_tab='params',
                            target_key=old_key
                        ).update({Comment.target_key: new_key}, synchronize_session=False)

    # Check for header key renames
    if 'headers' in data:
        old_headers = req.headers or []
        new_headers = data['headers'] or []
        old_map = {h['id']: h['key'].strip() for h in old_headers if 'id' in h and h.get('key')}
        for h in new_headers:
            if 'id' in h and h.get('key'):
                new_key = h['key'].strip()
                hid = h['id']
                if hid in old_map:
                    old_key = old_map[hid]
                    if old_key != new_key and new_key:
                        Comment.query.filter_by(
                            request_id=req.id,
                            target_tab='headers',
                            target_key=old_key
                        ).update({Comment.target_key: new_key}, synchronize_session=False)

    # Calculate diff before modifying
    before_diff = {}
    after_diff = {}
    for field in ['url', 'params', 'headers', 'body', 'auth']:
        if field in data:
            current_val = getattr(req, field)
            new_val = data[field]
            if current_val != new_val:
                before_diff[field] = current_val
                after_diff[field] = new_val

    if 'url'     in data: req.url     = data['url']
    if 'params'  in data: req.params  = data['params']
    if 'headers' in data: req.headers = data['headers']
    if 'body'    in data: req.body    = data['body']
    if 'auth'    in data: req.auth    = data['auth']
    
    if before_diff:
        log_activity(collection.workspace_id, user_id, 'request', 'update', 'request', req.name, req.id,
                     before_state=before_diff, after_state=after_diff)
                     
    db.session.commit()
    return {'id': req.id}, None


def delete_request(request_id, user_id):
    req = db.session.get(Request, request_id)
    if not req:
        return None, 'Request not found'

    collection = db.session.get(Collection, req.collection_id) if req.collection_id else None
    if not collection:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(collection.workspace_id, user_id)
    if not allowed:
        return None, err

    log_activity(collection.workspace_id, user_id, 'request', 'delete', 'request', req.name, req.id)
    db.session.delete(req)
    db.session.commit()
    return True, None
