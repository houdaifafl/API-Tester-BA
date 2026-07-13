1. Feature Summary
   Move database connection URI to environment variables (SEC-11).
   - **Backend**:
     - Modify config loading in `app.py` to read the database URI from the environment (`DATABASE_URL` or `SQLALCHEMY_DATABASE_URI`), using the legacy SQL Server string as a local development fallback.
     - Add `DATABASE_URL` configuration to environment templates (`.env` and `.env.example`).

2. Design Review
   2.1 Architecture Rationale
       - Hardcoded connection strings expose database structure and credentials, making deployment across environments rigid (violates 12-factor configuration guidelines). Loading it from the environment decouples code from configuration.
       - A default fallback preserves out-of-the-box local developer functionality while securing production deployments.

   2.2 State Ownership
       - Configuration variables are stateless and loaded at application startup.

   2.3 Service Ownership
       - Handled in `backend/app.py` factory initializer.

   2.4 Testing Strategy
       - Verify that setting the environment variable changes the database configuration in a test application instance.
       - Run all integration tests (which override DB config to SQLite in-memory) to verify zero regressions.

   2.5 Scalability Concerns
       - None.

3. Files to Create
   - None.

4. Files to Modify
   - **[MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)**
     - Load `SQLALCHEMY_DATABASE_URI` configuration from the environment.
   - **[MODIFY] [.env.example](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env.example)**
     - Document `DATABASE_URL` environment configuration variable template.
   - **[MODIFY] [.env](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/.env)**
     - Set default local `DATABASE_URL` environment variable.

5. API Contract Changes
   - None.

6. OpenAPI Spec Additions
   - None.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest` to assert no regressions.
   - **Manual Verification**:
     - Run a quick python verification check to confirm the environment variable loads correctly.
