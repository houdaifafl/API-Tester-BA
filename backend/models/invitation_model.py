from datetime import datetime
from models.base import db

class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    role = db.Column(db.String(20), nullable=False, default='viewer')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    workspace = db.relationship('Workspace', back_populates='invitations')
    inviter = db.relationship('User', foreign_keys=[inviter_id], back_populates='sent_invitations')
    invitee = db.relationship('User', foreign_keys=[invitee_id], back_populates='received_invitations')
