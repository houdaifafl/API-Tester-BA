# Secure JWT Cookie Migration (Fix SEC-04)

This plan details the migration of JWT token storage from browser `sessionStorage` (vulnerable to XSS extraction) to a secure, `httpOnly` cookie.

## User Review Required

> [!IMPORTANT]
> **Cross-Origin Cookie Configuration:** 
> Because the React frontend (running on `http://localhost:3000`) and the Flask backend (running on `http://localhost:5000`) are on different ports, we rely on CORS credential passing.
> - The backend CORS is already configured with `supports_credentials=True` (done in SEC-03).
> - The frontend `fetch` calls must explicitly use `credentials: 'include'` to send and receive the cookie.
> - In development, the cookie is set with `secure=False` since localhost uses HTTP. In production, `COOKIE_SECURE=True` must be set in the environment variables (e.g. `.env`) to enforce HTTPS.

## Design Review

### 2.1 Architecture Rationale
- **Security:** Moving the JWT from `sessionStorage` to a `httpOnly` cookie completely eliminates the risk of token theft via XSS. JavaScript running on the page cannot access `document.cookie` to read a cookie marked as `httpOnly`.
- **Backward Compatibility:** The backend decorator `token_required` will check for the `token` cookie first. If missing, it will check the `Authorization: Bearer <token>` header. This ensures existing unit/integration tests and third-party API clients do not break.
- **Session Management:** We will keep non-sensitive user metadata (`userId`, `username`, `email`, `isAdmin`) in `sessionStorage` so the React application knows a user is authenticated on page refresh. The actual secret credential (the token) is removed from `sessionStorage`.

### 2.2 State Ownership
No new state management components are introduced. The React frontend continues to track the logged-in user in `AuthContext` (local/feature level), but the `token` property will be set to `null` on the client side since JavaScript no longer has access to it.

### 2.3 Service Ownership
- **`authService.js`:** Modified to support credentials on `login` and `signup`. Added a new `logout` service call that triggers the backend logout route.
- **`api.js`:** Updated `authFetch` to always include `credentials: 'include'` on every request, ensuring the browser forwards the cookie automatically.

### 2.4 Testing Strategy
- **Backend integration tests:** We will add a new test file `backend/tests/test_cookie_auth.py` verifying that:
  - `/api/auth/login` sets the `token` cookie in response headers.
  - `/api/auth/logout` deletes/expires the `token` cookie.
  - Endpoints reject requests if the cookie is expired or invalid.
- **Manual Verification:** Confirm authentication flows in the browser (login, page refresh, logout). Inspect cookie headers and verify `httpOnly` flag is active in browser DevTools.

### 2.5 Scalability Concerns
None. Browser cookie storage is standard, highly optimized, and handled natively at the HTTP layer.

---

## Files to Create

### [NEW] [test_cookie_auth.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_cookie_auth.py)
- **Responsibility:** Integration tests for cookie-based authentication, verifying setting and deletion of cookies on login/logout.
- **Estimated Line Count:** ~40 lines.

---

## Files to Modify

### [MODIFY] [auth_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/auth_routes.py)
- Modify `/api/auth/login` to set the `token` cookie on the response with `httponly=True`, `samesite='Lax'`, and dynamic `secure` based on environment configuration.
- Add a new `/api/auth/logout` endpoint that deletes the `token` cookie and returns success.

### [MODIFY] [jwt_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/jwt_service.py)
- Update `token_required` decorator to retrieve token from `request.cookies.get('token')` before falling back to `Authorization` header.

### [MODIFY] [api.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/api.js)
- Update `authFetch` to include `credentials: 'include'` and remove manual `Authorization: Bearer <token>` header construction (since the browser handles the cookie automatically).

### [MODIFY] [authService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/authService.js)
- Update `login` and `signup` fetch requests to include `credentials: 'include'`.
- Add a new `logout()` service function that performs a `POST` request to `/api/auth/logout` with `credentials: 'include'`.

### [MODIFY] [AuthContext.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/contexts/AuthContext.js)
- Remove `token` fields from `useState` initialization and `logout` handler.
- In `logout`, call `authService.logout()` to delete the cookie on the backend.

### [MODIFY] [Login.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Login.js)
- Remove `sessionStorage.setItem('token', data.token)` and reference to `data.token` when calling `setUser`.

### [MODIFY] [.env](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env) & [.env.example](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env.example)
- Add `COOKIE_SECURE=false` (development default) and doc comments.

---

## API Contract Changes

### `POST /api/auth/login`
- **Request Body:** (unchanged)
- **Response Headers:**
  - `Set-Cookie: token=<JWT_STRING>; HttpOnly; SameSite=Lax; Path=/; Max-Age=86400`
- **Response Schema (200 OK):**
  - Removed `token` property from the JSON response body.

### `POST /api/auth/logout` [NEW]
- **Request Body:** `{}`
- **Response Headers:**
  - `Set-Cookie: token=; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT`
- **Response Schema (200 OK):**
  ```json
  {
    "message": "Logout successful"
  }
  ```

---

## OpenAPI Spec Additions

Modify `backend/openapi.yaml` to include the `/api/auth/logout` endpoint and document cookie auth:

```yaml
paths:
  /api/auth/logout:
    post:
      summary: Log out the active user and clear auth cookie
      responses:
        '200':
          description: Logout successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "Logout successful"

components:
  securitySchemes:
    CookieAuth:
      type: apiKey
      in: cookie
      name: token
```

---

## Rule Deviations
None. The implementation adheres fully to component separation, state/hook conventions, service architecture, and backend/frontend patterns.

---

## Verification Plan

### Automated Tests
Run backend integration tests:
```powershell
pytest backend/tests/test_cookie_auth.py
```

### Manual Verification
1. Open Chrome DevTools and go to Application -> Session Storage. Verify `token` is no longer saved.
2. Go to DevTools -> Application -> Cookies. Verify a cookie named `token` exists with a value, and the `HttpOnly` checkbox is checked.
3. Refresh the page; verify the user remains authenticated.
4. Click Logout; verify the `token` cookie is removed, and user is redirected to the login page.
