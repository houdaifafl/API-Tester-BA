from models.user_model import User
from models.workspace_model import Workspace
from models.base import db
from sqlalchemy import or_
from flask import current_app
import bcrypt

def signup_user(username, first_name, email, password):
    existing = User.query.filter(
        or_(User.username == username, User.email == email)
    ).first()
    if existing:
        if existing.username == username:
            return None, 'Username already exists'
        return None, 'Email already in use'

    rounds = 4 if current_app.config.get('TESTING') else 12
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
    user = User(username=username, first_name=first_name, email=email, password=hashed)
    db.session.add(user)
    db.session.flush()
    default_workspace = Workspace(name=f"{first_name}'s Space", user_id=user.id, is_default=True)
    db.session.add(default_workspace)
    db.session.commit()
    return user, None

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return None, 'Invalid username or password'
    return user, None
