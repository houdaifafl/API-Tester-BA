# Walkthrough — Collections List IDOR Protection (SEC-09)

This walkthrough documents the implementation and verification of authorization checks on the workspace collections list endpoint (SEC-09).

## Changes Made

### 1. Workspace Service Read Check
- **`backend/services/workspace_service.py`**:
  - Implemented `check_user_read_access(workspace_id, user_id)` to query the database and verify if the user is either the workspace owner or has an active membership.

### 2. Collection Service Refactoring
- **`backend/services/collection_service.py`**:
  - Updated `get_collections_by_workspace` signature to accept `user_id` and evaluate read access privileges via `check_user_read_access`.
  - Refactored the service return type to follow the standard `(result, error)` tuple model per Rule 7.3.

### 3. Route Access Enforcing
- **`backend/routes/collection_routes.py`**:
  - Updated the GET `/api/workspaces/<workspace_id>/collections` route handler to unpack the service return tuple.
  - Return `403 Forbidden` if access is denied, and `404 Not Found` if the workspace does not exist.

### 4. API Documentation
- **`backend/openapi.yaml`**:
  - Documented `403` and `404` response schemas for `GET /api/workspaces/{workspace_id}/collections`.

---

## Verification Results

### Integration Tests
All 203 backend tests passed successfully:
```powershell
backend\tests\test_collections.py ...........................            [100%]
...
===================== 203 passed, 464 warnings in 10.95s ======================
```
The newly added test cases inside `backend/tests/test_collections.py` verify that:
- Fetching collections for a workspace owned by another user without membership yields a `403 Forbidden` status.
- Fetching collections for a non-existent workspace ID yields `404 Not Found`.
- Authorized queries succeed normally with `200 OK`.
