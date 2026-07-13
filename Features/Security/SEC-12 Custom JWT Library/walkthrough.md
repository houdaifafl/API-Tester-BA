# Walkthrough — Standard PyJWT Integration (SEC-12)

This walkthrough documents the implementation and verification of standard, audited token signature verification and algorithm enforcement using PyJWT (SEC-12).

## Changes Made

### 1. Dependency Integration
- **`backend/requirements`**:
  - Registered `pyjwt` package dependency, ensuring it is automatically loaded by the application environment.

### 2. Service Refactoring
- **`backend/services/jwt_service.py`**:
  - Imported `jwt` and removed local `base64url_encode`, `base64url_decode`, `hmac`, and `hashlib` parsing helpers.
  - Refactored `encode_token` to generate the JWT via `jwt.encode(..., algorithm="HS256")`.
  - Refactored `decode_token` to verify signatures, check expiration (`exp`), and enforce the `"HS256"` algorithm via `jwt.decode(..., algorithms=["HS256"])` (blocking algorithm confusion attacks).
  - Mapped PyJWT verification exceptions (`jwt.ExpiredSignatureError`, `jwt.InvalidTokenError`) to API friendly error messages, maintaining complete compatibility with existing authorization route logic.

---

## Verification Results

### Integration Tests
All 211 backend tests passed successfully:
```powershell
===================== 211 passed, 472 warnings in 10.87s ======================
```
Verification confirmed:
-Preserved exact signature compatibility for auth controllers and integration testing suites.
- Valid tokens continue to grant access seamlessly.
- Signature validation failures, expired tokens, and invalid configurations are cleanly intercepted by PyJWT and map to standard `401 Unauthorized` responses.
