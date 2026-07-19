# Implementation Plan — Workspace Activity Feed & Audit Logging

chronological ledger of events (settings, collections, requests, membership, execution runs) for transparency and auditing.

---

## 1. Feature Summary
A collaborative workspace requires logs showing who modified requests, when collections were created, and who joined/left the space. We will build an activity feed with:
- **Automatic Audit Logging**: Captures actions on workspaces, collections, requests, collaborators, and run executions.
- **Role-Based Visibility Filtering**:
  - Owners and Editors see all activities.
  - Viewers see only collection actions, request edits, and execution logs.
- **Sensitive Data Redaction**: Automatic scrubbing of tokens, passwords, cookies, and keys.
- **Frontend Timeline & Diff Viewer**: Displays logs with a color-coded before/after diff inspector.

---

## 2. Design Review

### 2.1 Architecture Rationale
- **Decoupled Activity Logger**: Logging is implemented inside `backend/services/activity_service.py` to keep target services thin and maintain clean SRP.
- **Database Model**: We will create a `workspace_activities` table caching the target entity name so deleted requests or users still display their titles properly.
- **Centralized Redaction**: Diff sanitization is handled centrally prior to db write.

### 2.2 State Ownership
Follows the three-layer state model:
- **Global**: Auth token is read from `AuthContext` to identify active user.
- **Feature-level**: Active workspace state is managed in `MainPage` and passed to child tab panels.
- **Local UI**: The active tab in `OverviewPanel`, open/collapsed diff states in the timeline, and modal open states.

### 2.3 Service Ownership
- **`activity_service.py`**: Handles querying, formatting, diffing, and redacting logs.
- **Existing Services**: Hooked at successful execution boundaries (after commits) to trigger logging without blocking database flows.

### 2.4 Testing Strategy
- **Backend integration test** (`backend/tests/test_activities.py`):
  - Assertions for creation, update (only storing changed fields), and deletion logs.
  - Verification of Viewer access filter logic (restricted categories are hidden).
  - Validation of credentials scrubbing.
- **Frontend Smoke Test**: Check that `ActivityLogTab` renders timeline items.

### 2.5 Scalability Concerns
- Activity logs grow continuously. We limit query retrievals using standard SQL offsets and pagination (`limit=100`) to avoid response bloating.

---

## 3. Files to Create

- **[NEW] [activity_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/activity_model.py)** (Est: ~35 lines)
  - `WorkspaceActivity` database model.
- **[NEW] [activity_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/activity_service.py)** (Est: ~120 lines)
  - Core activity logger, payload diffing, credentials scrubbing, and listing filters.
- **[NEW] [activity_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/activity_routes.py)** (Est: ~35 lines)
  - Blueprint defining `GET /api/workspaces/<workspace_id>/activities`.
- **[NEW] [test_activities.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_activities.py)** (Est: ~90 lines)
  - Pytest tests checking logging, diffing, redaction, and viewer constraints.
- **[NEW] [activityService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/activityService.js)** (Est: ~15 lines)
  - Frontend client calling `/api/workspaces/{id}/activities`.
- **[NEW] [ActivityLogTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/ActivityLogTab.js)** (Est: ~100 lines)
  - Timeline component showing chronological feed.
- **[NEW] [ActivityLogTab.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/ActivityLogTab.css)** (Est: ~45 lines)
  - Styles for the timeline layout.
- **[NEW] [WorkspaceSettingsModal.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceSettingsModal.js)** (Est: ~110 lines)
  - Settings UI for renaming workspace and list/management of members/invitations.
- **[NEW] [WorkspaceSettingsModal.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceSettingsModal.css)** (Est: ~50 lines)
  - Styles for the settings modal.

---

## 4. Files to Modify

- **[MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)**
  - Register `activity_bp`. Add `workspace_activities` schema creation and auto-patches.
- **[MODIFY] [workspace_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/workspace_routes.py)**
  - Add `PATCH /api/workspaces/<workspace_id>` (rename), `PATCH /api/workspaces/<workspace_id>/members/<user_id>` (role edit), and `DELETE /api/workspaces/<workspace_id>/members/<user_id>` (remove member).
- **[MODIFY] [invitation_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/invitation_routes.py)**
  - Add `DELETE /api/invitations/<invitation_id>` (cancel pending invite).
- **[MODIFY] [workspace_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/workspace_service.py)**
  - Implement settings and member modification functions. Append `log_activity` calls.
- **[MODIFY] [invitation_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/invitation_service.py)**
  - Hook logging on invitation creation, accept, decline, and cancel.
- **[MODIFY] [collection_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/collection_service.py)**
  - Hook logging on collection creations, renames, updates, and deletes.
- **[MODIFY] [request_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/request_service.py)**
  - Hook logging on request creations, renames, parameter saves, and deletes.
- **[MODIFY] [history_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/history_service.py)**
  - Hook logging on request executions.
- **[MODIFY] [OverviewPanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/OverviewPanel.js)**
  - Add `Activity Log` tab and render the feed timeline.
- **[MODIFY] [MainPanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPanel.js)**
  - Pass workspace properties to `OverviewPanel`.
- **[MODIFY] [WorkspaceDropdown.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceDropdown.js)**
  - Bind "Settings" click to trigger the settings modal.
- **[MODIFY] [workspaceService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/workspaceService.js)**
  - Add API fetch endpoints for renaming, updating, and removing collaborators.
- **[MODIFY] [invitationService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/invitationService.js)**
  - Add cancel invitation API client endpoint.
- **[MODIFY] [openapi.yaml](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/openapi.yaml)**
  - Document the newly registered endpoints.

---

## 5. API Contract Changes

### 1. `GET /api/workspaces/<workspace_id>/activities`
- **Request**: JWT auth.
- **Response `200`**:
  ```json
  [
    {
      "id": 4,
      "user_username": "jane_doe",
      "event_category": "request",
      "action": "update",
      "target_type": "request",
      "target_name": "Get User Details",
      "before_state": {"url": "http://old.com"},
      "after_state": {"url": "http://new.com"},
      "created_at": "2026-07-15T20:46:00Z"
    }
  ]
  ```

### 2. `PATCH /api/workspaces/<workspace_id>`
- **Request Body**: `{"name": "New Name"}`
- **Response `200`**: `{"message": "Workspace renamed"}`

### 3. `DELETE /api/invitations/<invitation_id>`
- **Response `200`**: `{"message": "Invitation cancelled"}`

### 4. `PATCH /api/workspaces/<workspace_id>/members/<user_id>`
- **Request Body**: `{"role": "editor"}`
- **Response `200`**: `{"message": "Role updated"}`

### 5. `DELETE /api/workspaces/<workspace_id>/members/<user_id>`
- **Response `200`**: `{"message": "Member removed"}`

---

## 6. OpenAPI Spec Additions
Exposes path details for activities, rename, and collaborator modifications.

---

## 7. Rule Deviations
None.

---

## 8. Verification Plan

### Automated Tests
- Run `pytest backend/tests/test_activities.py` to verify logging behavior and sanitization checks.
- Run complete test suite `pytest` for regressions.

### Manual Verification
- Open Overview panel, select `Activity Log`.
- Perform request and collection modifications, accept invitations, and verify that the timeline updates. Toggle `[Show Diffs]` to inspect colored diff formats.
