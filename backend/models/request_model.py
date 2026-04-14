from backend.models.base import db
class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    method = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(500), nullable=False)

    params = db.Column(db.JSON)
    headers = db.Column(db.JSON)
    body = db.Column(db.JSON)

    collection_id = db.Column(
        db.Integer,
        db.ForeignKey('collections.id'),
        nullable=False)
