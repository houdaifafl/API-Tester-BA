from flask import Blueprint, request, jsonify, g
from services.auth_service import signup_user, login_user
from services.workspace_service import get_user_workspaces
from services.jwt_service import encode_token, token_required
from extensions import limiter
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/signup', methods=['POST'])
@limiter.limit("10 per minute")
def signup():
    data = request.json if request.is_json else {}
    username = data.get('username')
    first_name = data.get('first_name')
    email = data.get('email')
    password = data.get('password')

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not first_name:
        return jsonify({'error': 'First name is required'}), 400
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    if len(username) > 100:
        return jsonify({'error': 'Username exceeds maximum length of 100 characters'}), 400
    if len(first_name) > 100:
        return jsonify({'error': 'First name exceeds maximum length of 100 characters'}), 400
    if len(email) > 255:
        return jsonify({'error': 'Email exceeds maximum length of 255 characters'}), 400
    if len(password) > 72:
        return jsonify({'error': 'Password exceeds maximum length of 72 characters'}), 400

    _, error = signup_user(username, first_name, email, password)
    if error:
        return jsonify({'error': error}), 409

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.json if request.is_json else {}
    username = data.get('username')
    password = data.get('password')

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    if len(username) > 100:
        return jsonify({'error': 'Username exceeds maximum length of 100 characters'}), 400
    if len(password) > 72:
        return jsonify({'error': 'Password exceeds maximum length of 72 characters'}), 400

    user, error = login_user(username, password)
    if error:
        status = 403 if 'suspended' in error.lower() else 401
        return jsonify({'error': error}), status

    token = encode_token({'user_id': user.id, 'is_admin': user.is_admin})
    workspaces = get_user_workspaces(user.id)
    default_ws = next((w for w in workspaces if w['is_default']), workspaces[0] if workspaces else None)

    cookie_secure = os.environ.get('COOKIE_SECURE', 'false').lower() == 'true'

    response = jsonify({
        'message': 'Login successful',
        'token': token,  # kept in JSON for test/client backward compatibility
        'username': user.username,
        'user_id': user.id,
        'email': user.email,
        'is_admin': user.is_admin,
        'default_workspace_id': default_ws['id'] if default_ws else None,
    })

    # Set httpOnly cookie containing the token
    response.set_cookie(
        'token',
        token,
        httponly=True,
        secure=cookie_secure,
        samesite='Lax',
        max_age=86400  # 24 hours
    )

    return response, 200

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logout successful'})
    response.set_cookie('token', '', expires=0, httponly=True, samesite='Lax')
    return response, 200

@auth_bp.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    from models.base import db
    from models.user_model import User
    user = db.session.get(User, g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    }), 200
