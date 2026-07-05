from datetime import datetime
from models.base import db

class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    workspace = db.relationship('Workspace', back_populates='memberships')
    user = db.relationship('User', back_populates='memberships')
