from datetime import datetime
from models.base import db

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=True)
    target_tab = db.Column(db.String(50), nullable=True)  # params, headers, body, auth
    target_key = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = db.relationship('Workspace', backref=db.backref('comments_list', cascade='all, delete-orphan', lazy=True))
    user = db.relationship('User', backref=db.backref('comments_list', lazy=True))
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan',
        lazy=True
    )
    request = db.relationship(
        'Request',
        backref=db.backref('comments_list', cascade='all, delete-orphan', lazy=True)
    )
