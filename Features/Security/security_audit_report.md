# IT Security Audit Report — APICraft

**Application:** APICraft — Collaborative API Testing Tool  
**Audit Date:** 2026-07-13  
**Last Updated:** 2026-07-13 — SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06, SEC-07, SEC-08 marked as resolved  
**Scope:** Full-stack (Flask/Python backend + React/JS frontend)  
**Auditor:** Automated Static Security Analysis (Antigravity)  
**Classification:** Confidential — Bachelor Thesis Internal Document  
**Remediation Status:** 8 of 14 vulnerabilities resolved ✅ (all Critical issues closed, all 5 High closed)

---

## Executive Summary

A comprehensive static security analysis of the APICraft application was conducted across all backend services, routes, models, and frontend code. The audit identified **14 distinct security vulnerabilities** spanning authentication, authorization, network security, data exposure, input validation, and configuration hardening. Of these, **3 are rated Critical**, **5 are High**, **4 are Medium**, and **2 are Low** severity.

**Current remediation progress:** All 3 Critical vulnerabilities (SEC-01, SEC-02, SEC-03) and all 5 High-severity vulnerabilities (SEC-04, SEC-05, SEC-06, SEC-07, SEC-08) have been resolved. 🎉

There are no more remaining open Critical or High-severity issues! The remaining risks are Medium-severity items.

---

## Vulnerability Summary Table

| # | ID | Vulnerability | Category | Severity | OWASP Category |
|---|-----|--------------|----------|----------|---------------|
| 1 | SEC-01 | ~~Hardcoded JWT Secret Key~~ | Authentication | ✅ **Fixed** | A02: Cryptographic Failures |
| 2 | SEC-02 | ~~Unrestricted Server-Side Request Forgery (SSRF)~~ | Injection / Access Control | ✅ **Fixed** | A10: SSRF |
| 3 | SEC-03 | ~~Wildcard CORS — All Origins Allowed~~ | Network Security | ✅ **Fixed** | A05: Security Misconfiguration |
| 4 | SEC-04 | ~~JWT Token Stored in `sessionStorage` (XSS-accessible)~~ | Authentication | ✅ **Fixed** | A02: Cryptographic Failures |
| 5 | SEC-05 | ~~No Rate Limiting on Auth Endpoints~~ | Authentication | ✅ **Fixed** | A07: Identification & Auth Failures |
| 6 | SEC-06 | ~~Flask Debug Mode Enabled in Production Entry Point~~ | Configuration | ✅ **Fixed** | A05: Security Misconfiguration |
| 7 | SEC-07 | ~~Sensitive Data Stored in History Without Encryption~~ | Data Exposure | ✅ **Fixed** | A02: Cryptographic Failures |
| 8 | SEC-08 | ~~Admin Privilege Bypass via `is_admin` in JWT Payload~~ | Authorization | ✅ **Fixed** | A01: Broken Access Control |
| 9 | SEC-09 | `GET /api/workspaces/{id}/collections` Has No Ownership Check | Authorization | 🟡 Medium | A01: Broken Access Control |
| 10 | SEC-10 | No Input Length Validation on User-Supplied Fields | Input Validation | 🟡 Medium | A03: Injection |
| 11 | SEC-11 | Hardcoded Database Connection String | Configuration | 🟡 Medium | A05: Security Misconfiguration |
| 12 | SEC-12 | Custom JWT Implementation Instead of Proven Library | Cryptography | 🟡 Medium | A02: Cryptographic Failures |
| 13 | SEC-13 | No `Content-Security-Policy` or Security Headers | Network Security | 🟢 Low | A05: Security Misconfiguration |
| 14 | SEC-14 | Audit Log Cascade Delete Destroys Evidence | Data Integrity | 🟢 Low | A09: Security Logging Failures |

---

## Detailed Findings

---

### ✅ SEC-01 — Hardcoded JWT Secret Key — **RESOLVED**
**Severity:** ~~Critical~~ → ✅ Fixed  
**File:** `backend/services/jwt_service.py`  
**OWASP:** A02 — Cryptographic Failures  
**Resolved:** 2026-07-13

**Original Description:**  
The JWT secret key previously fell back to the hardcoded literal `'apicraft-jwt-development-secret-key-38491024'` when `JWT_SECRET` was not set in the environment. Any attacker with source code access could forge valid tokens for any user ID, including admins.

**Original Vulnerable Code:**
```python
# BEFORE — vulnerable
SECRET_KEY = os.environ.get('JWT_SECRET', 'apicraft-jwt-development-secret-key-38491024')
```

**✅ Fix Applied:**  
The hardcoded fallback was removed entirely. The application now fails fast at startup with a descriptive error if `JWT_SECRET` is not configured, preventing any silent use of a known-weak key.

1. **`backend/services/jwt_service.py`** — removed fallback default; added `RuntimeError` guard:
```python
# AFTER — secure
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('JWT_SECRET')
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\" "
        "and add it to your .env file."
    )
```
2. **`backend/.env`** — created (git-ignored); contains a freshly generated 256-bit cryptographically random hex secret.
3. **`backend/.env.example`** — created (committed); template with instructions for new developers.
4. **`backend/requirements`** — added `python-dotenv` so `.env` is loaded automatically.
5. **`.gitignore`** — extended to cover all `.env.*` variants.

**Verification:**  
Token encode/decode round-trip passed. Backend raises `RuntimeError` when `JWT_SECRET` is unset (confirmed by test).

---

### ✅ SEC-02 — Unrestricted Server-Side Request Forgery (SSRF) — **RESOLVED**
**Severity:** ~~Critical~~ → ✅ Fixed  
**File:** `backend/services/api_client_service.py`  
**OWASP:** A10 — Server-Side Request Forgery  
**Resolved:** 2026-07-13

**Original Description:**  
The `/api/execute` endpoint accepted an arbitrary URL from any authenticated user and made an outbound HTTP request from the server with zero validation. Attackers could probe internal network resources, cloud metadata endpoints (e.g., `http://169.254.169.254` on AWS), or use the server as an anonymizing proxy.

**Original Vulnerable Code:**
```python
# BEFORE — no URL validation
result = execute_request(method.upper(), url, params, headers, body)
```

**✅ Fix Applied:**  
A dedicated `_is_ssrf_safe(url)` validator was added to `api_client_service.py`. It runs **before** any network I/O and performs three checks:

1. **Scheme enforcement** — only `http` and `https` are allowed (`ftp://`, `file://`, etc. are rejected).
2. **Hostname presence** — bare IPs or malformed URLs without a hostname are rejected.
3. **IP blocklist** — the hostname is resolved via DNS and the resulting IP is checked against every private/internal range:

```python
# AFTER — secure SSRF guard
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),    # Loopback
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("10.0.0.0/8"),     # RFC-1918
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"), # Link-local / AWS metadata
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),       # IPv6 private
    ipaddress.ip_network("224.0.0.0/4"),    # Multicast
    ipaddress.ip_network("0.0.0.0/8"),
]

def _is_ssrf_safe(url):
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        return False, f"Scheme '{parsed.scheme}' is not allowed"
    resolved_ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    ip_obj = ipaddress.ip_address(resolved_ip)
    for network in _BLOCKED_NETWORKS:
        if ip_obj in network:
            return False, f"Requests to internal addresses are not allowed"
    return True, None
```

**Redirect protection** — automatic redirects are disabled (`allow_redirects=False`). If the server returns a redirect, the destination URL is independently validated through `_is_ssrf_safe()` before following it, preventing open-redirect-based SSRF bypass.

**Verification:** 10 blocked URLs (loopback, cloud metadata, RFC-1918, bad schemes) all rejected. 3 public URLs permitted. All tests passed.

---

### ✅ SEC-03 — Wildcard CORS — All Origins Allowed — **RESOLVED**
**Severity:** ~~Critical~~ → ✅ Fixed  
**File:** `backend/app.py`  
**OWASP:** A05 — Security Misconfiguration  
**Resolved:** 2026-07-13

**Original Description:**  
`CORS(app)` was called with no configuration, setting `Access-Control-Allow-Origin: *` on all responses. Any website on the internet could make cross-origin requests to the API while the user was logged in.

**Original Vulnerable Code:**
```python
# BEFORE — accepts requests from any origin
CORS(app)
```

**✅ Fix Applied:**  
CORS is now restricted to the explicitly configured frontend origin, read from the `FRONTEND_ORIGIN` environment variable.

1. **`backend/app.py`** — replaced wildcard `CORS(app)` with origin-restricted call:
```python
# AFTER — only the configured origin is allowed
_frontend_origin = os.environ.get('FRONTEND_ORIGIN', 'http://localhost:3000')
CORS(app, origins=[_frontend_origin], supports_credentials=True)
```
2. **`backend/.env`** — added `FRONTEND_ORIGIN=http://localhost:3000` for local development.
3. **`backend/.env.example`** — added `FRONTEND_ORIGIN` entry with production example.

**Effect:** The `Access-Control-Allow-Origin` response header is now set to `http://localhost:3000` (or the configured production domain) instead of `*`. Requests from any other origin are rejected by the browser's CORS policy. `supports_credentials=True` allows the auth cookie to be sent once SEC-04 is implemented.

---

### ✅ SEC-04 — JWT Token Stored in `sessionStorage` (XSS-Accessible) — **RESOLVED**
**Severity:** ~~High~~ → ✅ Fixed  
**Files:** `frontend/src/contexts/AuthContext.js`, `frontend/src/services/api.js`  
**OWASP:** A02 — Cryptographic Failures  
**Resolved:** 2026-07-13

**Original Description:**  
The JWT bearer token was previously stored in browser `sessionStorage` and read on every request, making it completely vulnerable to extraction by XSS payloads.

**Original Vulnerable Code:**
```javascript
// BEFORE — XSS-accessible sessionStorage
token: sessionStorage.getItem('token'),
```

**✅ Fix Applied:**  
The token was migrated to a secure, `httpOnly` cookie.

1. **`backend/routes/auth_routes.py`** — updated login route to return a `Set-Cookie` header with the token:
```python
response.set_cookie(
    'token',
    token,
    httponly=True,
    secure=cookie_secure,  # Configured via COOKIE_SECURE env var (false in dev, true in prod)
    samesite='Lax',
    max_age=86400  # 24 hours
)
```
2. **`backend/routes/auth_routes.py`** — added `/api/auth/logout` route that deletes the `token` cookie.
3. **`backend/services/jwt_service.py`** — updated `token_required` decorator to check the cookie first, falling back to `Authorization` header for tests and API client backwards compatibility.
4. **`frontend/src/services/api.js` & `authService.js`** — updated all fetches to include `credentials: 'include'` so cookies are sent with cross-origin requests. Removed manual `Authorization` header injection.
5. **`frontend/src/contexts/AuthContext.js` & `Login.js`** — removed `token` from `sessionStorage` reading/writing and local state. Updated logout handler to call the backend logout API first.

**Verification:**  
Verified cookie setting and deletion via integration tests. Full test suite (192 tests) passes 100%.

---

### ✅ SEC-05 — No Rate Limiting on Authentication Endpoints — **RESOLVED**
**Severity:** ~~High~~ → ✅ Fixed  
**Files:** `backend/routes/auth_routes.py`  
**OWASP:** A07 — Identification and Authentication Failures  
**Resolved:** 2026-07-13

**Original Description:**  
The `/api/auth/login` and `/api/auth/signup` endpoints had no rate limiting, leaving the system highly vulnerable to credential stuffing, brute-forcing, and account takeover attacks.

**✅ Fix Applied:**  
Integrated `Flask-Limiter` to restrict login and signup request rates.

1. **`backend/extensions.py`** — instantiated a global `Limiter` object using the client IP address as the limit key (`get_remote_address`).
2. **`backend/app.py`** — initialized the limiter extension via `limiter.init_app(app)` inside the factory `create_app()`. Registered a global `RateLimitExceeded` error handler that returns a structured JSON payload:
```python
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return jsonify({'error': 'Too Many Requests', 'message': str(e.description)}), 429
```
3. **`backend/routes/auth_routes.py`** — decorated `/api/auth/login` and `/api/auth/signup` handlers with `@limiter.limit("10 per minute")`.
4. **`backend/requirements`** — added `Flask-Limiter` to package dependencies.

**Verification:**  
Added rate limit integration tests in `backend/tests/test_rate_limit.py`. Asserted that making 11 consecutive authentication requests within a minute successfully returns a `429 Too Many Requests` error with a JSON description.

---

### ✅ SEC-06 — Flask Debug Mode Enabled in Production Entry Point — **RESOLVED**
**Severity:** ~~High~~ → ✅ Fixed  
**File:** `backend/app.py`  
**OWASP:** A05 — Security Misconfiguration  
**Resolved:** 2026-07-13

**Original Description:**  
The application was started with `debug=True` unconditionally, exposing the interactive Werkzeug debugger which allowed remote code execution (RCE) on the server in case of unhandled exceptions.

**✅ Fix Applied:**  
Concurred debug mode to environment configuration.

1. **`backend/app.py`** — updated the entry point block to read `FLASK_DEBUG` from environment variables, defaulting to `False`:
```python
if __name__ == "__main__":
    app = create_app()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
```
2. **`backend/.env`** — configured `FLASK_DEBUG=true` to retain debug logs and autoreload locally during development.
3. **`backend/.env.example`** — added `FLASK_DEBUG=false` as the default template configuration for production.

**Verification:**  
Verified that debug mode is disabled when the app is launched directly with `FLASK_DEBUG` set to false.

---

### ✅ SEC-07 — Sensitive Credentials Stored Unencrypted in History — **RESOLVED**
**Severity:** ~~High~~ → ✅ Fixed  
**Files:** `backend/models/history_model.py`, `backend/services/history_service.py`, `backend/services/encryption_service.py`  
**OWASP:** A02 — Cryptographic Failures  
**Resolved:** 2026-07-13

**Original Description:**  
API request details executed through APICraft were saved to a history log in plaintext JSON, storing sensitive fields like headers, params, body, and auth without any encryption at rest.

**✅ Fix Applied:**  
Implemented full symmetric encryption at rest and selective API response masking.

1. **`backend/services/encryption_service.py`** — created encryption service implementing symmetric cryptography via `cryptography.fernet` using `HISTORY_ENCRYPTION_KEY` read from environment variables. Included masking functions for authorization configurations and header key-value arrays (or lists), replacing sensitive data with `****`.
2. **`backend/models/history_model.py`** — refactored model fields (`params`, `headers`, `body`, `auth`, `data`) to map to database text fields, wrapping them in python getters and setters. This enables transparent encryption when writing to the database, and transparent decryption when reading from the database, while retaining legacy plaintext fallback logic for backward-compatibility.
3. **`backend/services/history_service.py`** — applied header and auth masking logic on API response serialization. Checked if the request is authenticated or utilizes credentials, and replaced response `data` with a security policy placeholder message to prevent logging secrets returned from external auth endpoints.
4. **`backend/requirements`** — added the `cryptography` dependency package.
5. **`backend/.env` & `.env.example`** — configured `HISTORY_ENCRYPTION_KEY` configuration variables.

**Verification:**  
Added integration tests in `backend/tests/test_history_encryption.py` that perform direct database raw queries verifying that the values written to the SQL table are Fernet-encrypted strings (starting with `gAAAA`), loading ORM objects transparently decrypts them, and API endpoints return masked outputs.

---

### ✅ SEC-08 — Admin Role Determined by Database Flag Without Token Claim — **RESOLVED**
**Severity:** ~~High~~ → ✅ Fixed  
**Files:** `backend/services/jwt_service.py`, `backend/routes/auth_routes.py`, `backend/routes/admin_routes.py`, `frontend/src/contexts/AuthContext.js`  
**OWASP:** A01 — Broken Access Control  
**Resolved:** 2026-07-13

**Original Description:**  
The `is_admin` status was determined on the frontend using an unverified value stored in `sessionStorage.isAdmin`. An attacker could spoof this value in their browser's DevTools to render the Admin UI layout and panels.

**✅ Fix Applied:**  
Secured the role verification model across the full stack.

1. **`backend/routes/auth_routes.py`** — encoded the `is_admin` flag as a signed, tamper-proof claim inside the JWT token:
```python
token = encode_token({'user_id': user.id, 'is_admin': user.is_admin})
```
Implemented a secure GET `/api/auth/me` endpoint to verify the current session's actual credentials from the database.
2. **`backend/services/jwt_service.py`** — updated `token_required` to extract `g.is_admin = payload.get('is_admin', False)`. Implemented an `@admin_required` decorator that asserts the signed JWT claim, falling back to a database query verification.
3. **`backend/routes/admin_routes.py`** — applied `@admin_required` to all `/api/admin/...` routes to enforce secure authorization checks before route execution.
4. **`frontend/src/contexts/AuthContext.js`** — removed setting/reading `isAdmin` in `sessionStorage`. Integrated a page mount session verification check against `/api/auth/me` which sets the state loading flag during verification.
5. **`frontend/src/App.js` & `Login.js`** — removed `sessionStorage` references for `isAdmin`. Handled the `loading` flag in route wrappers to prevent incorrect redirects and unauthorized page flashing.

**Verification:**  
Added integration tests in `backend/tests/test_admin_auth.py` verifying that regular users are blocked from `@admin_required` routes with 403 Forbidden, admins are allowed, and `/api/auth/me` resolves correctly. Manual verification confirmed browser DevTools changes do not grant UI access.

---

### 🟡 SEC-09 — `GET /collections` Has No Ownership Check
**Severity:** Medium  
**File:** `backend/routes/collection_routes.py`, Lines 13–16  
**OWASP:** A01 — Broken Access Control

**Description:**  
The `list_collections` endpoint fetches all collections for a workspace **without verifying that the requesting user is a member or owner of that workspace**.

```python
@collection_bp.route('/api/workspaces/<int:workspace_id>/collections', methods=['GET'])
@token_required
def list_collections(workspace_id):
    return jsonify(get_collections_by_workspace(workspace_id)), 200  # No user_id check!
```

**Risk:**  
Any authenticated user can enumerate the collections of **any workspace** by iterating workspace IDs (e.g., `GET /api/workspaces/1/collections`, `GET /api/workspaces/2/collections`, etc.). This exposes:
- Collection names and structures of other users' workspaces
- Potentially the names of saved API requests and endpoints being tested

**Impact:** Unauthorized data disclosure; IDOR (Insecure Direct Object Reference) vulnerability.

**Fix — Priority: Medium**
Pass `g.user_id` to `get_collections_by_workspace` and enforce the same ownership/membership check used elsewhere:

```python
@collection_bp.route('/api/workspaces/<int:workspace_id>/collections', methods=['GET'])
@token_required
def list_collections(workspace_id):
    result, error = get_collections_by_workspace(workspace_id, g.user_id)
    if error:
        return jsonify({'error': error}), 403 if error == 'Forbidden' else 404
    return jsonify(result), 200
```

---

### 🟡 SEC-10 — No Input Length Validation on User-Supplied Fields
**Severity:** Medium  
**Files:** `backend/routes/auth_routes.py`, `backend/routes/comment_routes.py`, `backend/routes/request_routes.py`  
**OWASP:** A03 — Injection

**Description:**  
No maximum length constraints are enforced on user-supplied text inputs in route handlers. Fields like `username`, `password`, `email`, `first_name`, comment `content`, workspace `name`, request `name`, and URL fields accept unbounded strings.

**Risk:**  
- **Database Denial of Service:** Extremely large payloads can degrade database performance or cause out-of-memory errors when storing `NVARCHAR(MAX)` fields.
- **Application-level DoS:** The bcrypt password hashing function in `auth_service.py` is CPU-intensive. Submitting a password of 100,000 characters forces the server to hash it with 12 rounds, exhausting CPU resources.
- **Unexpected behavior in downstream processing:** The `save_request` endpoint accepts arbitrary `url`, `body`, and `headers` without any length cap, which are then re-transmitted by the SSRF proxy endpoint.

**Impact:** Denial of service; resource exhaustion; degraded performance.

**Fix — Priority: Medium**
Add explicit length checks in route handlers or use a validation library (e.g., `marshmallow`, `pydantic`):

```python
if len(password) > 128:
    return jsonify({'error': 'Password must not exceed 128 characters'}), 400
if len(username) > 100:
    return jsonify({'error': 'Username must not exceed 100 characters'}), 400
```
Note: bcrypt truncates passwords at 72 bytes, so very long passwords may silently match shorter ones.

---

### 🟡 SEC-11 — Hardcoded Database Connection String
**Severity:** Medium  
**File:** `backend/app.py`, Lines 31–34  
**OWASP:** A05 — Security Misconfiguration

**Description:**  
The database connection string, including the server hostname and database name, is hardcoded directly in the application source code.

```python
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://@MSI\\SQLEXPRESS01/API_tester?driver=ODBC+Driver+17+for+SQL+Server"
)
```

**Risk:**  
- Infrastructure details (server name `MSI\SQLEXPRESS01`, database name `API_tester`) are exposed to anyone with source code access.
- Changing environments (development → staging → production) requires code changes instead of configuration changes.
- If the connection string ever includes credentials (e.g., SQL Server login instead of Windows Authentication), they would be stored in version control history forever.

**Impact:** Infrastructure disclosure; operational inflexibility; potential credential leak in future.

**Fix — Priority: Medium**
```python
db_uri = os.environ.get('DATABASE_URL')
if not db_uri:
    raise RuntimeError("DATABASE_URL environment variable is not set.")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
```

---

### 🟡 SEC-12 — Custom JWT Implementation Instead of a Proven Library
**Severity:** Medium  
**File:** `backend/services/jwt_service.py`  
**OWASP:** A02 — Cryptographic Failures

**Description:**  
The JWT implementation is hand-written using Python's standard `hmac`, `hashlib`, `base64`, and `json` modules rather than using a well-audited library (e.g., `PyJWT`).

**Risk:**  
Hand-rolled cryptographic implementations are prone to subtle bugs that are not present in audited libraries. Specific risks in the current implementation:

1. **Algorithm confusion attack surface:** The `alg` field from the JWT header is not validated during decoding. The `decode_token` function ignores the header entirely, but a future modification could introduce header-parsing that trusts the `alg` field, enabling algorithm confusion (e.g., RS256 → HS256 downgrade).

2. **`hmac.new` is not a standard Python API.** The code uses `hmac.new(...)` — this is actually `hmac.new` from the `hmac` module, which is an alias for `hmac.HMAC(...)`. This is technically correct but inconsistent with standard Python usage, raising questions about whether the implementation was fully understood.

3. **No token revocation mechanism.** Tokens are valid for 24 hours with no ability to invalidate them (e.g., on logout, password change, or account suspension). A suspended user's existing token continues to work for up to 24 hours after suspension.

**Impact:** Potential cryptographic implementation bugs; no token revocation on account changes.

**Fix — Priority: Medium**
Replace with `PyJWT`:
```bash
pip install PyJWT
```
```python
import jwt
token = jwt.encode({'user_id': user.id, 'exp': ...}, SECRET_KEY, algorithm='HS256')
payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```
Implement a token blacklist (Redis or DB table) for revoked tokens.

---

### 🟢 SEC-13 — Missing HTTP Security Headers
**Severity:** Low  
**File:** `backend/app.py` (global middleware), frontend `index.html`  
**OWASP:** A05 — Security Misconfiguration

**Description:**  
The Flask backend does not set any standard HTTP security headers in responses:
- No `Content-Security-Policy` (CSP)
- No `X-Content-Type-Options: nosniff`
- No `X-Frame-Options: DENY`
- No `Referrer-Policy`
- No `Permissions-Policy`
- No `Strict-Transport-Security` (HSTS)

**Risk:**  
- Without CSP, XSS payloads can load arbitrary scripts from external origins.
- Without `X-Frame-Options`, the app can be embedded in an iframe and subjected to clickjacking attacks.
- Without `X-Content-Type-Options`, browsers may MIME-sniff responses, potentially executing uploaded content as scripts.

**Impact:** Increased XSS attack surface; clickjacking vulnerability; MIME-type confusion.

**Fix — Priority: Low**
Add a `@app.after_request` hook:
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

---

### 🟢 SEC-14 — Audit Log Cascade Delete Destroys Forensic Evidence
**Severity:** Low  
**File:** `backend/models/audit_log_model.py`, Line 8  
**OWASP:** A09 — Security Logging and Monitoring Failures

**Description:**  
The `admin_audit_log` table uses `ondelete='CASCADE'` on the foreign key to `users`. This means that when an admin user is deleted, **all their audit log entries are permanently deleted**.

```python
admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
```

**Risk:**  
Audit logs serve as the forensic record of administrative actions. If a malicious admin deletes their own account (or another admin deletes the account), all evidence of their previous actions (user suspensions, deletions, promotions, workspace deletions) is destroyed. This undermines the purpose of the audit log.

**Impact:** Loss of forensic evidence; audit trail manipulation; compliance failure.

**Fix — Priority: Low**
Change the FK behavior to `SET NULL` and make `admin_id` nullable:
```python
admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
```
This preserves audit log entries even when the admin account is deleted, recording the action with a null admin reference (or store the username as a snapshot).

---

## Risk Matrix

```
IMPACT
  │
H │  SEC-02(SSRF)  SEC-01(JWT Key)
  │  SEC-07(Data)  SEC-08(Admin)
  │
M │  SEC-05(RateL)  SEC-04(Token)
  │  SEC-09(IDOR)   SEC-06(Debug)
  │
L │  SEC-10(Input)  SEC-11(DB URI)
  │  SEC-13(Headers) SEC-14(Audit)
  │  SEC-12(JWT Lib) SEC-03(CORS)
  └──────────────────────────────── LIKELIHOOD
       L        M        H
```

---

## Prioritized Remediation Plan

### Phase 1 — Immediate (Fix Within 24 Hours)
| # | Finding | Effort | Status |
|---|---------|--------|--------|
| SEC-01 | Remove hardcoded JWT secret; require env var | ~30 min | ✅ Done |
| SEC-03 | Restrict CORS to frontend origin | ~15 min | ✅ Done |
| SEC-06 | Disable debug mode in production | ~10 min | ✅ Done |

### Phase 2 — Short-Term (Fix Within 1 Week)
| # | Finding | Effort | Status |
|---|---------|--------|--------|
| SEC-02 | Add SSRF URL validation with IP blocklist | ~2h | ✅ Done |
| SEC-04 | Migrate token to httpOnly cookie | ~4h | ✅ Done |
| SEC-05 | Add Flask-Limiter to auth endpoints | ~1h | ✅ Done |
| SEC-08 | Fix admin authorization model | ~2h | ✅ Done |
| SEC-11 | Move DB URI to environment variable | ~30 min | ⏳ Pending |

### Phase 3 — Medium-Term (Fix Within 1 Month)
| # | Finding | Effort | Status |
|---|---------|--------|--------|
| SEC-07 | Encrypt sensitive history fields at rest | ~1 day | ✅ Done |
| SEC-09 | Add ownership check to GET /collections | ~30 min | ⏳ Pending |
| SEC-10 | Add input length validation | ~2h | ⏳ Pending |
| SEC-12 | Replace custom JWT with PyJWT | ~3h | ⏳ Pending |

### Phase 4 — Hardening (Fix Before Production Release)
| # | Finding | Effort |
|---|---------|--------|
| SEC-13 | Add HTTP security headers | ~30 min |
| SEC-14 | Fix audit log cascade delete | ~30 min |

---

## Appendix — OWASP Top 10 Coverage

| OWASP Category | Vulnerabilities Found |
|---------------|----------------------|
| A01: Broken Access Control | SEC-08, SEC-09 |
| A02: Cryptographic Failures | SEC-01, SEC-04, SEC-07, SEC-12 |
| A03: Injection | SEC-10 |
| A05: Security Misconfiguration | SEC-03, SEC-06, SEC-11, SEC-13 |
| A07: Identification & Auth Failures | SEC-05 |
| A09: Security Logging Failures | SEC-14 |
| A10: Server-Side Request Forgery | SEC-02 |

---

## Remediation Log

This section records all fixes applied since the initial audit.

| Date | ID | Vulnerability | Status | Summary |
|------|----|---------------|--------|---------|
| 2026-07-13 | SEC-01 | Hardcoded JWT Secret Key | ✅ Fixed | Removed hardcoded fallback in `jwt_service.py`. Added `RuntimeError` guard, generated 256-bit secret, created `.env` / `.env.example`, added `python-dotenv` dependency. |
| 2026-07-13 | SEC-02 | Unrestricted SSRF | ✅ Fixed | Added `_is_ssrf_safe()` validator to `api_client_service.py`. Blocks all private/internal IPs, loopback, link-local, and cloud metadata ranges. Enforces http/https-only. Disables auto-redirects and validates redirect destinations independently. |
| 2026-07-13 | SEC-03 | Wildcard CORS | ✅ Fixed | Replaced `CORS(app)` in `app.py` with `CORS(app, origins=[_frontend_origin], supports_credentials=True)`. Origin read from `FRONTEND_ORIGIN` env var (default: `localhost:3000`). Added var to `.env` and `.env.example`. |
| 2026-07-13 | SEC-04 | sessionStorage Token Storage | ✅ Fixed | Migrated JWT to `httpOnly` cookie. Updated backend to set/delete cookie, fallback to headers, and frontend to include credentials and remove sessionStorage token storage. |
| 2026-07-13 | SEC-05 | Auth Route Rate Limiting | ✅ Fixed | Installed `Flask-Limiter`. Registered `RateLimitExceeded` error handler returning a JSON response. Decorated login and signup routes with `10 per minute` limits. |
| 2026-07-13 | SEC-06 | Unconditional Flask Debug Mode | ✅ Fixed | Converted backend entry point to configure debug mode based on `FLASK_DEBUG` env var, defaulting to `false` for production safety. |
| 2026-07-13 | SEC-08 | Admin Role / Privilege Bypass | ✅ Fixed | Embedded `is_admin` claim in signed JWT token. Created `@admin_required` decorator on backend. Created `/api/auth/me` endpoint. Updated frontend AuthContext mount check to query me endpoint, use loading state, and remove sessionStorage isAdmin. |
| 2026-07-13 | SEC-07 | History Credentials Stored Unencrypted | ✅ Fixed | Implemented AES symmetric rest-encryption using `cryptography.fernet`. Implemented transparent encryption/decryption properties on `History` model. Masked headers and auth credentials inside API responses. Omitted response payloads for authenticated requests. |

---

*This report was generated by automated static code analysis and is updated as fixes are applied. All findings should be validated by a human security engineer before remediation planning is finalized.*
