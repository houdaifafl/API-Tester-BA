1. Feature Summary
   Implement robust role-based access control and verify admin status securely (SEC-08).
   - **Backend**: Include the `is_admin` status as a claim in the JWT token payload. Implement a new `@admin_required` decorator that validates the `is_admin` claim (with database fallback), and use it for all `/api/admin/...` endpoints. Implement a protected `/api/auth/me` endpoint to return the current authenticated user's profile and verified admin status.
   - **Frontend**: Remove reliance on unsafe `sessionStorage.isAdmin` for rendering decisions. Fetch verified credentials from `/api/auth/me` on application mount, displaying a clean loading state before resolving routes.

2. Design Review
   2.1 Architecture Rationale
       - JWT tokens are cryptographically signed on the backend using the server's private `JWT_SECRET`. Adding the `is_admin` claim to the token payload ensures role assertions are secure and tamper-proof.
       - Centralizing the check in an `@admin_required` decorator simplifies routes and reduces database lookups by validating the signed token claim directly, while retaining a database fallback check for ultimate safety.
       - Fetching credentials on page load (`/api/auth/me`) ensures that any manual local storage or sessionStorage tampering by a user in DevTools is automatically overridden by a verified server assertion before rendering components.

   2.2 State Ownership
       - The user's authenticated identity and verified admin status will be managed globally in the frontend React application's `AuthContext` (Global state layer per Section 3.1).
       - A `loading` state will be introduced in `AuthContext` during the bootstrap check, preventing premature route redirects.

   2.3 Service Ownership
       - A new `/api/auth/me` route will be added to the auth domain services and routes (`auth_routes.py` and `authService.js`).

   2.4 Testing Strategy
       - Write a new integration test suite `backend/tests/test_admin_auth.py` asserting that:
         - Regular users are rejected with `403 Forbidden` on admin endpoints decorated with `@admin_required`.
         - Admins are allowed to access those endpoints.
         - `/api/auth/me` returns correct details for regular users and admins.
       - Add component smoke tests to ensure context updates do not crash the app.

   2.5 Scalability Concerns
       - Validating the `is_admin` claim directly from the cryptographically verified JWT token saves a database query on every admin API request.

3. Files to Create
   - **[NEW] [test_admin_auth.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_admin_auth.py)** (Est: ~40 lines)
     - Test cases verifying `@admin_required` protection and `/api/auth/me` endpoint.

4. Files to Modify
   - **[MODIFY] [jwt_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/jwt_service.py)**
     - In `token_required`, read `is_admin` claim from payload and store in `g.is_admin`.
     - Implement `@admin_required` decorator checking `g.is_admin` with database fallback.
   - **[MODIFY] [auth_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/auth_routes.py)**
     - In `login()` and `signup()`, encode the `is_admin` claim into the JWT payload.
     - Implement `/api/auth/me` GET endpoint.
   - **[MODIFY] [admin_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/admin_routes.py)**
     - Import `@admin_required` from `services.jwt_service` and apply it to all `/api/admin/...` endpoints instead of `@token_required`. Keep `@token_required` on notification endpoints.
   - **[MODIFY] [authService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/authService.js)**
     - Add `getMe()` function.
   - **[MODIFY] [AuthContext.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/contexts/AuthContext.js)**
     - Add `loading` state to provider.
     - Fetch user info on mount via `getMe()`.
     - Remove setting/getting of `isAdmin` inside `sessionStorage`.
   - **[MODIFY] [Login.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Login.js)**
     - Remove saving `isAdmin` to `sessionStorage` on login.
   - **[MODIFY] [App.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/App.js)**
     - Update `ProtectedRoute` and `AdminRoute` helper components to return a Loading indicator while the bootstrap session check is in-flight.

5. API Contract Changes
   - `/api/auth/me` (GET):
     - Headers: `Authorization: Bearer <token>` or httpOnly Cookie.
     - Response schema (200):
       ```json
       {
         "user_id": 123,
         "username": "alice",
         "email": "alice@example.com",
         "is_admin": true
       }
       ```
     - Response schema (401):
       ```json
       {
         "error": "Unauthorized"
       }
       ```

6. OpenAPI Spec Additions
   - Add `/api/auth/me` path definition to `backend/openapi.yaml`.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_admin_auth.py`
     - Run all backend tests to ensure backward compatibility.
   - **Manual Verification**:
     - Log in as a regular user, try to open the browser console and type `sessionStorage.setItem('isAdmin', 'true')` and refresh. Verify that the app immediately redirects the user back to the workspace and does not render the Admin Dashboard.
     - Log in as an admin, verify the Admin page displays correctly and works on refresh.
