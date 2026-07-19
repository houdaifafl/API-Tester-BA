from datetime import datetime
from models.base import db

class WorkspaceActivity(db.Model):
    __tablename__ = 'workspace_activities'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_category = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_name = db.Column(db.String(255), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    before_state = db.Column(db.JSON, nullable=True)
    after_state = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workspace = db.relationship('Workspace', backref=db.backref('activities', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='activities')

    def to_dict(self):
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'user_id': self.user_id,
            'user_username': self.user.username if self.user else 'Unknown',
            'event_category': self.event_category,
            'action': self.action,
            'target_type': self.target_type,
            'target_name': self.target_name,
            'target_id': self.target_id,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'created_at': self.created_at.isoformat() + 'Z'
        }
