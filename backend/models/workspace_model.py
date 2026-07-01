from models.base import db

class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_default = db.Column(db.Boolean, nullable=False, default=False, server_default='0')

    collections = db.relationship('Collection', backref='workspace', lazy=True, cascade='all, delete-orphan')
    history_entries = db.relationship('History', back_populates='workspace', lazy=True, cascade='all, delete-orphan')

