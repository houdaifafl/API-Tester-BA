from models.collection_model import Collection
from models.request_model import Request
from models.base import db


def _serialize(c):
    return {
        'id': c.id,
        'name': c.name,
        'is_default': c.is_default,
        'requests': [
            {
                'id':      r.id,
                'name':    r.name,
                'method':  r.method,
                'url':     r.url or '',
                'params':  r.params,
                'headers': r.headers,
                'body':    r.body,
                'auth':    r.auth,
            }
            for r in c.requests
        ],
    }


def ensure_default_collection(workspace_id):
    exists = Collection.query.filter_by(workspace_id=workspace_id).first()
    if not exists:
        collection = Collection(name='My Collection', workspace_id=workspace_id, is_default=True)
        db.session.add(collection)
        db.session.flush()
        db.session.add(Request(name='Get data',  method='GET',  url='', collection_id=collection.id))
        db.session.add(Request(name='Post data', method='POST', url='', collection_id=collection.id))
        db.session.commit()


def get_collections_by_workspace(workspace_id, user_id):
    from services.workspace_service import check_user_read_access
    allowed, err = check_user_read_access(workspace_id, user_id)
    if not allowed:
        return None, err

    ensure_default_collection(workspace_id)
    collections = Collection.query.filter_by(workspace_id=workspace_id).all()
    return [_serialize(c) for c in collections], None



def add_collection(workspace_id, user_id):
    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(workspace_id, user_id)
    if not allowed:
        return None, err

    collection = Collection(name='New Collection', workspace_id=workspace_id, is_default=False)
    db.session.add(collection)
    db.session.commit()
    return _serialize(collection), None


def rename_collection(collection_id, new_name, user_id):
    col = db.session.get(Collection, collection_id)
    if not col:
        return None, 'Collection not found'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(col.workspace_id, user_id)
    if not allowed:
        return None, err

    col.name = new_name
    db.session.commit()
    return _serialize(col), None


def delete_collection(collection_id, user_id):
    col = db.session.get(Collection, collection_id)
    if not col:
        return None, 'Collection not found'
    if col.is_default:
        return None, 'Cannot delete the default collection'

    from services.workspace_service import check_user_write_access
    allowed, err = check_user_write_access(col.workspace_id, user_id)
    if not allowed:
        return None, err

    db.session.delete(col)
    db.session.commit()
    return True, None
