from models.base import db

class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)

    requests = db.relationship('Request', backref='collection', lazy=True)