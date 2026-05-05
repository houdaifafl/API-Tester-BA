from models.request_model import Request
from models.collection_model import Collection
from models.base import db


def create_request(collection_id):
    collection = Collection.query.get(collection_id)
    if not collection:
        return None, 'Collection not found'

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
    db.session.commit()

    return {
        'id': new_request.id,
        'name': new_request.name,
        'method': new_request.method,
        'url': new_request.url,
        'collection_id': new_request.collection_id,
    }, None


def rename_request(request_id, new_name):
    req = Request.query.get(request_id)
    if not req:
        return None, 'Request not found'
    req.name = new_name
    db.session.commit()
    return {'id': req.id, 'name': req.name}, None


def delete_request(request_id):
    req = Request.query.get(request_id)
    if not req:
        return None, 'Request not found'
    db.session.delete(req)
    db.session.commit()
    return True, None
