from backend.models.base import db

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    requests = db.relationship('Request', backref='collection', lazy=True)