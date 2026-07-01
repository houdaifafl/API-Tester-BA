from datetime import datetime
from models.base import db

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    
    params = db.Column(db.JSON, nullable=True)
    headers = db.Column(db.JSON, nullable=True)
    body = db.Column(db.JSON, nullable=True)
    auth = db.Column(db.JSON, nullable=True)
    
    status = db.Column(db.Integer, nullable=True)
    response_time = db.Column(db.Float, nullable=True)
    data = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to Workspace
    workspace = db.relationship('Workspace', back_populates='history_entries')
