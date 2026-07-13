1. Feature Summary
   Replace hand-rolled JWT implementation with PyJWT (SEC-12).
   - **Backend**:
     - Add `pyjwt` dependency package to `backend/requirements` and install it.
     - Refactor `backend/services/jwt_service.py` to utilize `jwt.encode` and `jwt.decode` (configured to strictly enforce the `"HS256"` signing algorithm).
     - Maintain exact API compatibility for `encode_token` and `decode_token` interfaces.

2. Design Review
   2.1 Architecture Rationale
       - Custom cryptographic protocols are prone to subtle implementation bugs (timing attacks, validation bypasses). Using `PyJWT` enforces standardized, audited signature verification and expiration handling.
       - Enforcing `algorithms=["HS256"]` during token decoding prevents algorithm confusion attacks (e.g. key/algorithm confusion).

   2.2 State Ownership
       - No new state is introduced.

   2.3 Service Ownership
       - Authenticating and authorization checks reside in `jwt_service.py`.

   2.4 Testing Strategy
       - Run all existing integration tests. Since `encode_token` and `decode_token` signatures are preserved, all tests (such as cookie authentication and token verification) should pass without any modification.
       - Verify exception decoding logic (e.g., expiration errors) maps cleanly to the expected error string responses.

   2.5 Scalability Concerns
       - None. `PyJWT` has high performance and is industry-standard.

3. Files to Create
   - None.

4. Files to Modify
   - **[MODIFY] [requirements](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/requirements)**
     - Register `pyjwt` package dependency.
   - **[MODIFY] [jwt_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/jwt_service.py)**
     - Replace standard base64/hmac encoder/decoder functions with PyJWT interfaces.

5. API Contract Changes
   - None.

6. OpenAPI Spec Additions
   - None.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest` to assert 100% test coverage and functionality passes.
