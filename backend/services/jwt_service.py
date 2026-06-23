import hmac
import hashlib
import base64
import json
import time
import os
from functools import wraps
from flask import request, jsonify, g

SECRET_KEY = os.environ.get('JWT_SECRET', 'apicraft-jwt-development-secret-key-38491024')

def base64url_encode(payload_bytes):
    return base64.urlsafe_b64encode(payload_bytes).rstrip(b'=').decode('utf-8')

def base64url_decode(payload_str):
    padding = '=' * (4 - len(payload_str) % 4)
    return base64.urlsafe_b64decode((payload_str + padding).encode('utf-8'))

def encode_token(payload, expires_in=86400):
    """
    Generates a signed JWT token with a given expiration time (default 24h).
    """
    header = {"alg": "HS256", "typ": "JWT"}
    token_payload = dict(payload)
    token_payload["exp"] = int(time.time()) + expires_in
    
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(token_payload).encode('utf-8'))
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_token(token):
    """
    Decodes and validates the signature and expiration of a JWT token.
    Returns (payload, None) on success, or (None, error_message) on failure.
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, "Invalid token format"
        
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_signature_b64 = base64url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None, "Signature verification failed"
        
        payload = json.loads(base64url_decode(payload_b64).decode('utf-8'))
        if int(time.time()) > payload.get("exp", 0):
            return None, "Token expired"
        
        return payload, None
    except Exception as e:
        return None, f"Token decoding failed: {str(e)}"

def token_required(f):
    """
    Flask route decorator to enforce JWT authentication.
    Injects g.user_id on success, or returns 401 Unauthorized on failure.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized: Token is missing or invalid'}), 401
        
        token = auth_header.split(' ')[1]
        payload, error = decode_token(token)
        if error:
            return jsonify({'error': f'Unauthorized: {error}'}), 401
        
        g.user_id = payload.get('user_id')
        if not g.user_id:
            return jsonify({'error': 'Unauthorized: Invalid token payload'}), 401
            
        return f(*args, **kwargs)
    return decorated
