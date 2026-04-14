from backend.models.collection_model import Collection
from backend.models.base import db

def create_collection(name):
    try:
        new_collection = Collection(name=name)

        db.session.add(new_collection)
        db.session.commit()

        return {
            'id': new_collection.id,
            'name': new_collection.name,
        }
    except Exception as e:
        db.session.rollback()
        return None