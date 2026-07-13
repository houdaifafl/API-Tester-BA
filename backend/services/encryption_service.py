import os
import json
from cryptography.fernet import Fernet

# Read HISTORY_ENCRYPTION_KEY from environment, with a safe development fallback
_key = os.environ.get('HISTORY_ENCRYPTION_KEY')
if not _key:
    # Stable fallback key for development / testing context
    _key = "PRsIXLQQhPc3zGE4m_WP5izS7sDJHVo3xJMHjB0jcWA="

cipher_suite = Fernet(_key.encode('utf-8'))

def encrypt_val(val):
    """
    Encrypts a JSON-serializable python value (dict, list, string, etc.) to a cipher string.
    """
    if val is None:
        return None
    val_str = json.dumps(val)
    return cipher_suite.encrypt(val_str.encode('utf-8')).decode('utf-8')

def decrypt_val(cipher_str):
    """
    Decrypts a cipher string back to its original JSON value.
    Handles legacy unencrypted values gracefully.
    """
    if cipher_str is None:
        return None
    try:
        dec_bytes = cipher_suite.decrypt(cipher_str.encode('utf-8'))
        return json.loads(dec_bytes.decode('utf-8'))
    except Exception:
        # Fallback for legacy database entries that were stored in plaintext JSON
        try:
            return json.loads(cipher_str)
        except Exception:
            return cipher_str

def mask_sensitive_headers(headers):
    """
    Masks credentials or tokens in HTTP header list or dictionary.
    """
    if not headers:
        return headers
    
    sensitive_keys = {'authorization', 'proxy-authorization', 'x-api-key', 'apikey', 'token', 'secret', 'cookie', 'set-cookie'}
    
    if isinstance(headers, list):
        masked = []
        for h in headers:
            if isinstance(h, dict) and 'key' in h and 'value' in h:
                k = h['key']
                v = h['value']
                if k and k.lower() in sensitive_keys:
                    masked_h = dict(h)
                    if isinstance(v, str):
                        if v.lower().startswith('bearer '):
                            masked_h['value'] = 'Bearer ****'
                        elif v.lower().startswith('basic '):
                            masked_h['value'] = 'Basic ****'
                        else:
                            masked_h['value'] = '****'
                    else:
                        masked_h['value'] = '****'
                    masked.append(masked_h)
                else:
                    masked.append(h)
            else:
                masked.append(h)
        return masked
        
    elif isinstance(headers, dict):
        masked = {}
        for k, v in headers.items():
            if k.lower() in sensitive_keys:
                if isinstance(v, str):
                    if v.lower().startswith('bearer '):
                        masked[k] = 'Bearer ****'
                    elif v.lower().startswith('basic '):
                        masked[k] = 'Basic ****'
                    else:
                        masked[k] = '****'
                else:
                    masked[k] = '****'
            else:
                masked[k] = v
        return masked
        
    return headers

def mask_sensitive_auth(auth):
    """
    Masks credentials inside authorization config dictionaries.
    """
    if not auth:
        return auth
    masked = dict(auth)
    auth_type = auth.get('type')
    if auth_type == 'bearer':
        if 'bearer' in masked:
            masked['bearer'] = dict(masked['bearer'])
            if 'token' in masked['bearer']:
                masked['bearer']['token'] = '****'
    elif auth_type == 'basic':
        if 'basic' in masked:
            masked['basic'] = dict(masked['basic'])
            if 'password' in masked['basic']:
                masked['basic']['password'] = '****'
    elif auth_type == 'apikey':
        if 'apikey' in masked:
            masked['apikey'] = dict(masked['apikey'])
            if 'value' in masked['apikey']:
                masked['apikey']['value'] = '****'
    return masked

def should_mask_response_data(history_data):
    """
    Checks if a history request item contains credentials or request auth,
    implying the response content may contain secrets and shouldn't be logged.
    """
    headers = history_data.get('headers') or []
    auth = history_data.get('auth')
    
    sensitive_keys = {'authorization', 'proxy-authorization', 'x-api-key', 'apikey', 'token', 'secret', 'cookie', 'set-cookie'}
    
    if auth and auth.get('type') and auth.get('type') != 'none':
        return True
        
    if isinstance(headers, list):
        for h in headers:
            if isinstance(h, dict) and 'key' in h:
                k = h['key']
                if k and k.lower() in sensitive_keys:
                    return True
    elif isinstance(headers, dict):
        for k in headers.keys():
            if k.lower() in sensitive_keys:
                return True
            
    # Also scan response data itself for sensitive-looking keys (if dictionary)
    resp_data = history_data.get('data')
    if isinstance(resp_data, dict):
        def scan_dict(d):
            for k, v in d.items():
                if any(sk in k.lower() for sk in ['token', 'password', 'secret', 'passwd', 'session']):
                    return True
                if isinstance(v, dict):
                    if scan_dict(v):
                        return True
            return False
        if scan_dict(resp_data):
            return True
            
    return False
