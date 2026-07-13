# Walkthrough — Rate Limiting & Safe Debug Mode (SEC-05 & SEC-06)

This walkthrough documents the implementation and verification of authentication rate limiting (SEC-05) and conditional Flask debug mode (SEC-06).

## Changes Made

### 1. Dependencies & Configuration
- **`backend/requirements`**: Added `Flask-Limiter` to package dependencies.
- **`backend/extensions.py`**: Created a new file to instantiate a global `Limiter` instance to prevent circular imports. Uses client IP (`get_remote_address`) as keying function and a standard default limit.
- **`backend/.env` & `.env.example`**: Configured `FLASK_DEBUG` variable (default: `true` in dev, `false` in prod template).

### 2. Backend Middleware & Routes
- **`backend/app.py`**:
  - Initialized `limiter` using `limiter.init_app(app)`.
  - Registered a global error handler for `RateLimitExceeded` exceptions to return a standardized JSON body with a 429 status code.
  - Adjusted the script entry block to run Flask dynamically based on `FLASK_DEBUG`.
- **`backend/routes/auth_routes.py`**: Applied the `@limiter.limit("10 per minute")` rate limit decorator to the `login` and `signup` handlers.

### 3. Testing & Documentation
- **`backend/tests/test_rate_limit.py`**: Added new integration tests validating that:
  - Exceeding 10 auth attempts in a minute results in a `429 Too Many Requests` response.
  - Rate limit hits return a structured JSON response instead of default HTML.
  - Requests within the limits succeed normally.
- **`backend/tests/conftest.py`**: Updated the test app fixture to initialize `limiter` and register the `RateLimitExceeded` handler, matching production environment behavior.
- **`backend/openapi.yaml`**: Documented `429 Too Many Requests` responses and schemes on the login and signup paths.
- **`security_audit_report.md`**: Marked SEC-05 and SEC-06 as RESOLVED.

---

## Verification Results

### Integration Tests
All 194 integration tests passed successfully:
```powershell
backend\tests\test_rate_limit.py ..                                      [ 64%]
...
====================== 194 passed, 453 warnings in 9.13s ======================
```
The newly added rate limit test cases (`test_login_rate_limiting` and `test_signup_rate_limiting`) verify that the system correctly enforces the limits and replies with structured JSON payload.
