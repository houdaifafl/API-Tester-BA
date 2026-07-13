from datetime import datetime
from models.base import db
from services.encryption_service import encrypt_val, decrypt_val

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    
    # Store encrypted string in the database column
    _params = db.Column('params', db.Text, nullable=True)
    _headers = db.Column('headers', db.Text, nullable=True)
    _body = db.Column('body', db.Text, nullable=True)
    _auth = db.Column('auth', db.Text, nullable=True)
    _data = db.Column('data', db.Text, nullable=True)
    
    status = db.Column(db.Integer, nullable=True)
    response_time = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship to Workspace
    workspace = db.relationship('Workspace', back_populates='history_entries')

    # Transparent encryption/decryption properties
    @property
    def params(self):
        return decrypt_val(self._params)

    @params.setter
    def params(self, value):
        self._params = encrypt_val(value)

    @property
    def headers(self):
        return decrypt_val(self._headers)

    @headers.setter
    def headers(self, value):
        self._headers = encrypt_val(value)

    @property
    def body(self):
        return decrypt_val(self._body)

    @body.setter
    def body(self, value):
        self._body = encrypt_val(value)

    @property
    def auth(self):
        return decrypt_val(self._auth)

    @auth.setter
    def auth(self, value):
        self._auth = encrypt_val(value)

    @property
    def data(self):
        return decrypt_val(self._data)

    @data.setter
    def data(self, value):
        self._data = encrypt_val(value)

