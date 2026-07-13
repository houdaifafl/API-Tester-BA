# Walkthrough — Database Connection String Environment Migration (SEC-11)

This walkthrough documents the implementation and verification of environment-configured database connections (SEC-11).

## Changes Made

### 1. Dynamic Config Loading
- **`backend/app.py`**:
  - Replaced the hardcoded SQL Server connection string with an environment loader.
  - Queries `DATABASE_URL` (standard SQLAlchemy env variable name) or `SQLALCHEMY_DATABASE_URI` at startup.
  - Falls back to local MSSQL string for out-of-the-box Windows SQL Server local testing if no variable is present.

### 2. Environment Templates
- **`backend/.env.example`**:
  - Documented `DATABASE_URL` as a configurable parameter, indicating standard options for local SQL Server and local SQLite fallbacks.
- **`backend/.env`**:
  - Configured the active local development variable to target local SQL Server:
    `DATABASE_URL=mssql+pyodbc://@MSI\SQLEXPRESS01/API_tester?driver=ODBC+Driver+17+for+SQL+Server`

---

## Verification Results

### Integration Tests
All 211 backend tests passed successfully:
```powershell
===================== 211 passed, 472 warnings in 10.95s ======================
```
Verification confirmed:
- Setting the environment variable successfully overrides the database configuration.
- The default fallback preserves legacy local DB launch behaviors.
- The unit test suite continues to override to in-memory SQLite (`sqlite:///:memory:`) dynamically during setup.
