from flask import Blueprint, request, jsonify
from services.auth_service import signup_user, login_user
from services.workspace_service import get_user_workspaces
from services.jwt_service import encode_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/signup', methods=['POST'])
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

    _, error = signup_user(username, first_name, email, password)
    if error:
        return jsonify({'error': error}), 409

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json if request.is_json else {}
    username = data.get('username')
    password = data.get('password')

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400

    user, error = login_user(username, password)
    if error:
        return jsonify({'error': error}), 401

    token = encode_token({'user_id': user.id})
    workspaces = get_user_workspaces(user.id)
    default_ws = next((w for w in workspaces if w['is_default']), workspaces[0] if workspaces else None)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'username': user.username,
        'user_id': user.id,
        'email': user.email,
        'default_workspace_id': default_ws['id'] if default_ws else None,
    }), 200
