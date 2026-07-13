# Walkthrough — Audit Log Forensic Retention (SEC-14)

This walkthrough documents the implementation and verification of forensic audit log retention constraints (SEC-14).

## Changes Made

### 1. Database Schema Hardening
- **`backend/models/user_model.py`**:
  - Removed `cascade='all, delete-orphan'` from the User model `audit_logs` relationship. This prevents SQLAlchemy from cleaning up or deleting child logs when a parent User record is deleted.
- **`backend/models/audit_log_model.py`**:
  - Refactored `admin_id` column to be nullable (`nullable=True`) and modified its foreign key constraint to `ondelete='SET NULL'`.
  - Added a new column `admin_username = db.Column(db.String(100), nullable=True)` to directly store the admin's username at log generation time.
  - Adjusted `to_dict()` to prioritize the static `admin_username` column, falling back to dynamic relationship checking or `'Unknown'` only if the log is pre-existing without a username.

### 2. Log Generation Enhancement
- **`backend/services/admin_service.py`**:
  - Refactored the `_write_audit_log` helper to query the database for the active admin user and populate the new `admin_username` column during instantiation.

### 3. Startup Schema Migration
- **`backend/app.py`**:
  - Appended `admin_username` schema updates using `safe_add_column`.
  - Registered a database modification block for non-SQLite instances (SQL Server) to:
    - Alter `admin_id` to allow null values (`ALTER COLUMN admin_id INT NULL`).
    - Detect and drop existing cascade foreign keys.
    - Establish the new `ON DELETE SET NULL` constraint.

---

## Verification Results

### Integration Tests
All 213 backend integration tests passed successfully:
```powershell
backend\tests\test_audit_forensics.py .                                  [ 12%]
...
===================== 213 passed, 477 warnings in 10.70s ======================
```
The newly created integration test suite `backend/tests/test_audit_forensics.py` verifies that:
1. Creating an action registers an audit log referencing the executing admin user.
2. Deleting the executing admin user succeeds.
3. The audit log persists in the database despite the admin account's deletion.
4. The log holds a `NULL` admin reference (`admin_id = None`) while retaining the correct admin username (`admin_username = 'admin_forensic_test'`) in the query response.
