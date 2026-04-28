from models.user_model import User
from models.base import db
from werkzeug.security import generate_password_hash, check_password_hash

def signup_user(username, first_name, email, password):
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'
    if User.query.filter_by(email=email).first():
        return None, 'Email already in use'

    user = User(username=username, first_name=first_name, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user, None

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return None, 'Invalid username or password'
    return user, None
