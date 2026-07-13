1. Feature Summary
   Implement security hardening for backend endpoints by addressing SEC-05 (Authentication Rate Limiting) and SEC-06 (Unconditional Flask Debug Mode).
   - **SEC-05**: Protect authentication routes (`/api/auth/login` and `/api/auth/signup`) from brute-force and credential stuffing attacks by implementing `Flask-Limiter` to enforce a rate limit of 10 requests per minute per IP.
   - **SEC-06**: Restrict Flask debug mode in production by reading `FLASK_DEBUG` from environment variables, defaulting to `False`.

2. Design Review
   2.1 Architecture Rationale
       - `Flask-Limiter` will be used for rate limiting since it is the standard, well-tested package for Flask applications.
       - To prevent circular imports between `app.py` and route blueprints, the `Limiter` object will be instantiated in a dedicated extensions file (`backend/extensions.py`) and initialized inside the application factory `create_app()` in `backend/app.py`.
       - Flask debug mode will be driven by environment configuration (`FLASK_DEBUG`) instead of being hardcoded to `True` in the entry point.

   2.2 State Ownership
       - The rate limiting state (IP addresses, request counts, and timestamps) will be managed in-memory using `Flask-Limiter`'s default in-memory storage provider (`memory://`). No database tables are required.

   2.3 Service Ownership
       - Rate limiting is handled at the routing/middleware level by the Flask-Limiter package.
       - Blueprints (`auth_routes.py`) will import the `limiter` instance to apply route-specific limit decorators.

   2.4 Testing Strategy
       - Write a new integration test file `backend/tests/test_rate_limit.py`.
       - Test that consecutive auth requests beyond the rate limit (10 per minute) return a `429 Too Many Requests` status code.
       - Verify that valid requests within the limit succeed.
       - Test that debug mode is correctly disabled when `FLASK_DEBUG=false`.

   2.5 Scalability Concerns
       - In-memory storage for `Flask-Limiter` is perfect for single-instance web servers (typical for this thesis project setup). If the app is scaled horizontally behind a load balancer in the future, it can be seamlessly configured to use a Redis storage backend via the `RATELIMIT_STORAGE_URI` configuration key without changing any application code.

3. Files to Create
   - **[NEW] [extensions.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/extensions.py)** (Est: ~10 lines)
     - Instantiate the `limiter` object using `get_remote_address` as the key function.

4. Files to Modify
   - **[MODIFY] [requirements](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/requirements)**
     - Add `Flask-Limiter` to dependencies.
   - **[MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)**
     - Import and initialize `limiter` using `limiter.init_app(app)`.
     - Read `FLASK_DEBUG` from environment variables in `__main__` entry point to dynamically configure debug mode.
   - **[MODIFY] [.env](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env)** & **[.env.example](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env.example)**
     - Add `FLASK_DEBUG=true` to enable debug mode in local development.
   - **[MODIFY] [auth_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/auth_routes.py)**
     - Import `limiter` and decorate the `signup` and `login` route handlers with `@limiter.limit("10 per minute")`.

5. API Contract Changes
   - `/api/auth/login` (POST): Will return `429 Too Many Requests` if an IP exceeds 10 requests per minute.
     - Response schema (429):
       ```json
       {
         "error": "Too Many Requests"
       }
       ```
   - `/api/auth/signup` (POST): Will return `429 Too Many Requests` if an IP exceeds 10 requests per minute.
     - Response schema (429): Same as above.

6. OpenAPI Spec Additions
   - Add a `429` response schema to the `/api/auth/login` and `/api/auth/signup` routes in `backend/openapi.yaml`.

7. Rule Deviations
   - None. Follows all rules in Sections 2-10 of `AGENTS.md`.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_rate_limit.py` to assert that 11 requests in quick succession trigger a `429` error on the 11th request.
     - Run the full test suite to ensure no regressions.
   - **Manual Verification**:
     - Start the backend server and simulate rapid login attempts using curl or a scripting tool to see the 429 response block.
     - Verify debug mode is disabled on startup when `FLASK_DEBUG` environment variable is set to `false`.
