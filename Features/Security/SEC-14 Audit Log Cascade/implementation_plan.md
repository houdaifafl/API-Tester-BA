1. Feature Summary
   Prevent deletion of admin accounts from destroying associated forensic evidence logs (SEC-14).
   - **Backend Models**:
     - Update `AdminAuditLog` (`models/audit_log_model.py`):
       - Set `admin_id` column to `nullable=True` and configure foreign key relation `ondelete='SET NULL'`.
       - Add `admin_username = db.Column(db.String(100), nullable=True)` to persist the admin's username at log creation time.
       - Update `to_dict()` to return `self.admin_username` or fallback.
     - Update `User` (`models/user_model.py`):
       - Remove `cascade='all, delete-orphan'` from the `audit_logs` relationship.
   - **Backend Services**:
     - Update `_write_audit_log` in `services/admin_service.py` to retrieve the admin user's username and write it to the `admin_username` column.
   - **Database Setup**:
     - In `backend/app.py`, execute migration operations for SQL Server to make `admin_id` nullable, update the foreign key to `SET NULL` on delete, and add the `admin_username` column.

2. Design Review
   2.1 Architecture Rationale
       - Hard cascading deletes on audit logs allow a malicious admin or compromised account to delete themselves (or have another admin delete them) and destroy all traces of their activities.
       - Decoupling user records from log integrity via `ondelete='SET NULL'` and persisting `admin_username` inside the log table preserves a permanent, immutable audit trail for incident analysis.

   2.2 State Ownership
       - No new state is introduced.

   2.3 Service Ownership
       - The logic to log actions is centralized inside `admin_service.py`.

   2.4 Testing Strategy
       - Write a new integration test class `TestAuditLogForensicRetention` inside `backend/tests/test_admin.py` or a dedicated test file `backend/tests/test_audit_forensics.py` that:
         - Creates an admin user.
         - Performs an admin action (e.g. suspend a user) to write an audit log.
         - Deletes the admin user.
         - Verifies that the audit log record still exists in the database.
         - Verifies that `admin_id` is set to `None` / `NULL`.
         - Verifies that the log dictionary returned by `to_dict()` contains the deleted admin's username (preserving evidence).

   2.5 Scalability Concerns
       - None.

3. Files to Create
   - **[NEW] [test_audit_forensics.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_audit_forensics.py)** (Est: ~40 lines)
     - Forensic log retention integration tests.

4. Files to Modify
   - **[MODIFY] [user_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/user_model.py)**
     - Remove cascade constraints on `audit_logs` relation.
   - **[MODIFY] [audit_log_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/audit_log_model.py)**
     - Configure `admin_id` as nullable, add `admin_username`, update relationship options, and adjust `to_dict()`.
   - **[MODIFY] [admin_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/admin_service.py)**
     - In `_write_audit_log`, fetch admin details to save `admin_username`.
   - **[MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)**
     - Add database schema migrations to update foreign keys and add `admin_username` column.

5. API Contract Changes
   - None.

6. OpenAPI Spec Additions
   - None.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_audit_forensics.py`
     - Run all backend integration tests to verify no regressions.
