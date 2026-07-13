from datetime import datetime
from models.base import db

class AdminAuditLog(db.Model):
    __tablename__ = 'admin_audit_log'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    admin_username = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    target_snapshot = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    admin = db.relationship('User', back_populates='audit_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_username': self.admin_username or (self.admin.username if self.admin else 'Unknown'),
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_snapshot': self.target_snapshot,
            'created_at': self.created_at.isoformat() + 'Z'
        }
