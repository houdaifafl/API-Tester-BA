import time
import os
import jwt
from functools import wraps
from flask import request, jsonify, g
from dotenv import load_dotenv

# Load .env file if present (development convenience)
load_dotenv()

SECRET_KEY = os.environ.get('JWT_SECRET')
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\" "
        "and add it to your .env file or environment."
    )

def encode_token(payload, expires_in=86400):
    """
    Generates a signed JWT token with a given expiration time (default 24h).
    """
    token_payload = dict(payload)
    token_payload["exp"] = int(time.time()) + expires_in
    return jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    """
    Decodes and validates the signature and expiration of a JWT token.
    Returns (payload, None) on success, or (None, error_message) on failure.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError as e:
        return None, f"Invalid token: {str(e)}"
    except Exception as e:
        return None, f"Token decoding failed: {str(e)}"

def token_required(f):
    """
    Flask route decorator to enforce JWT authentication.
    Injects g.user_id on success, or returns 401 Unauthorized on failure.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # SEC-04: Try Authorization header first (tests, API clients)
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # Fallback to httpOnly cookie (standard browser/web app UI requests)
        if not token:
            token = request.cookies.get('token')
                
        if not token:
            return jsonify({'error': 'Unauthorized: Token is missing or invalid'}), 401
        
        payload, error = decode_token(token)
        if error:
            return jsonify({'error': f'Unauthorized: {error}'}), 401
        
        g.user_id = payload.get('user_id')
        g.is_admin = payload.get('is_admin', False)
        if not g.user_id:
            return jsonify({'error': 'Unauthorized: Invalid token payload'}), 401
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """
    Decorator to restrict access to administrators only.
    Checks the 'is_admin' claim in the verified JWT token (with database validation fallback).
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        is_admin = getattr(g, 'is_admin', False)
        if not is_admin:
            from models.base import db
            from models.user_model import User
            user = db.session.get(User, g.user_id)
            if not (user and user.is_admin):
                return jsonify({'error': 'Forbidden: Admin privilege required'}), 403
            g.is_admin = True
        return f(*args, **kwargs)
    return decorated

