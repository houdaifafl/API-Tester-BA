from models.base import db
from models.audit_log_model import AdminAuditLog
from models.notification_model import UserNotification

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_suspended = db.Column(db.Boolean, default=False, nullable=False)

    workspaces = db.relationship('Workspace', backref='owner', lazy=True, cascade='all, delete-orphan')

    # Relationships
    memberships = db.relationship('WorkspaceMember', back_populates='user', lazy=True, cascade='all, delete-orphan')
    sent_invitations = db.relationship('Invitation', foreign_keys='Invitation.inviter_id', back_populates='inviter', lazy=True, cascade='all, delete-orphan')
    received_invitations = db.relationship('Invitation', foreign_keys='Invitation.invitee_id', back_populates='invitee', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AdminAuditLog', back_populates='admin', lazy=True)
    notifications = db.relationship('UserNotification', back_populates='user', lazy=True, cascade='all, delete-orphan')
