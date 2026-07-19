# Walkthrough — Workspace Activity Feed & Audit Logging

This walkthrough documents the implementation and verification details of the **Workspace Activity Feed & Audit Logging** feature.

---

## 1. Summary of Changes

We implemented a robust audit logging ledger and feed in both backend and frontend layers.

### 1.1 Backend Implementation
- **Database Model**: Created `WorkspaceActivity` mapping to the `workspace_activities` table in [`backend/models/activity_model.py`](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit%20API%20tester/backend/models/activity_model.py). Caches target metadata to support displays of deleted entities.
- **Service Hooks**: Hooked `log_activity` into:
  - `workspace_service.py`: Logging workspace creations, deletes, and renames.
  - `invitation_service.py`: Logging collaborator invites, cancels, accepts, and declines.
  - `collection_service.py`: Logging collection creations, renames, and deletions.
  - `request_service.py`: Logging request creations, renames, parameter changes, and deletions.
  - `history_service.py`: Logging execution runs (stores HTTP response code and response latency).
- **Credentials Sanitization**: Implemented automatic pattern matching in `backend/services/activity_service.py` to scrub keys matching `authorization`, `bearer`, `cookie`, `set-cookie`, `x-api-key`, `api_key`, `token`, `password`, `secret` with `[REDACTED]` values.
- **Routes & Blueprints**:
  - Registered `activity_bp` endpoint `/api/workspaces/<workspace_id>/activities` in `app.py`.
  - Added collaborator listing and settings management endpoints (`GET /collaborators`, `PATCH /members/<id>`, `DELETE /members/<id>`).

### 1.2 Frontend Implementation
- **Timeline Component**: Created [`ActivityLogTab.js`](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/ActivityLogTab.js) to query activities and render chronological feeds with color-coded diff markers (red for deletions, green for additions).
- **Settings Modal Dialog**: Created [`WorkspaceSettingsModal.js`](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceSettingsModal.js) to manage settings (renaming workspace) and collaborators (role updates, removal, cancelling pending invitations).

---

## 2. Verification Results

We verified the complete feature using the **three-tier testing strategy**.

### Tier 1 — Backend pytest Integration Tests
We wrote 5 new integration tests verifying successful retrieval, forbidden access attempts, collection modifications logging, credentials scrubbing, and viewer access limitations.
All 221 integration tests in the suite passed:
```
backend/tests/test_activities.py .....                                   [100%]
===================== 221 passed, 1033 warnings in 19.44s =====================
```

### OpenAPI drift test
The automated OpenAPI drift tests verify that all endpoints correspond 100% to the active Flask registry routes, ensuring zero drift.
