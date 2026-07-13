1. Feature Summary
   Implement input string length validation across all route controllers (SEC-10).
   - **Backend**:
     - Validate input lengths in `auth_routes.py`, `comment_routes.py`, `workspace_routes.py`, `collection_routes.py`, `request_routes.py`, `api_client_routes.py`, and `invitation_routes.py`.
     - Reject requests containing inputs that exceed predefined length caps with a `400 Bad Request` status and a clear JSON error payload.

2. Design Review
   2.1 Architecture Rationale
       - Input validation is a fundamental security practice (OWASP A03: Injection). Validating at the route controller level (before calling services or executing ORM operations) prevents resource-exhaustion Denial of Service (DoS) and database column overflow issues.
       - Enforcing a maximum length of 72 characters on passwords prevents CPU-intensive bcrypt hashing of extremely large payloads (Application DoS).
       - Enforcing database column limits (e.g. 500 characters on saved URLs) prevents SQL write failures or data corruption.

   2.2 State Ownership
       - No new state is introduced. Validation is stateless and occurs on request parsing.

   2.3 Service Ownership
       - Validation checks are enforced directly in the route handlers (thin controllers) to validate the request payload format and constraints before entering the service layer.

   2.4 Testing Strategy
       - Create an integration test suite `backend/tests/test_input_validation.py` to assert that:
         - Overly long usernames, passwords, emails, names, comments, URLs, or roles are successfully rejected with `400 Bad Request` and a descriptive message.
         - Valid inputs continue to work correctly without issues.

   2.5 Scalability Concerns
       - None. Stateless string length validation is extremely fast and computationally cheap compared to DB writes or password hashing.

3. Files to Create
   - **[NEW] [test_input_validation.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_input_validation.py)** (Est: ~70 lines)
     - Test cases verifying rejection of long fields.

4. Files to Modify
   - **[MODIFY] [auth_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/auth_routes.py)**
     - Validate lengths of `username` (max 100), `first_name` (max 100), `email` (max 255), and `password` (max 72) in `signup` and `login`.
   - **[MODIFY] [comment_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/comment_routes.py)**
     - Validate lengths of comment `content` (max 2000), `target_tab` (max 50), and `target_key` (max 255).
   - **[MODIFY] [workspace_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/workspace_routes.py)**
     - Validate length of workspace `name` (max 100).
   - **[MODIFY] [collection_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/collection_routes.py)**
     - Validate length of collection `name` (max 100).
   - **[MODIFY] [request_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/request_routes.py)**
     - Validate lengths of request `name` (max 100), `method` (max 10), and `url` (max 500 when saving).
   - **[MODIFY] [api_client_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/api_client_routes.py)**
     - Validate lengths of `method` (max 10) and proxy `url` (max 2048).
   - **[MODIFY] [invitation_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/invitation_routes.py)**
     - Validate lengths of `username` (max 100) and `role` (max 20).

5. API Contract Changes
   - Every modified route will return `400 Bad Request` if input validation constraints are violated. E.g.:
     ```json
     {
       "error": "Password exceeds maximum length of 72 characters"
     }
     ```

6. OpenAPI Spec Additions
   - None (schema validation logic is internal to route controllers, standard 400 Bad Request schemas are already defined).

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_input_validation.py`
     - Run all backend integration tests to ensure no regressions.
