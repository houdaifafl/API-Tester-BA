# Implement APICraft Super Admin Features

This plan details the architecture, design decisions, database additions, API routes, and frontend layouts required to support the global **Super Admin** role in APICraft.

---

## User Review Required

> [!IMPORTANT]
> **Database Seed/Migration**:
> - We will add two new columns to the `users` table: `is_admin` (default `False`) and `is_suspended` (default `False`).
> - We will create two new models/tables: `admin_audit_log` (for tracking admin actions) and `user_notifications` (for notifying users of suspensions/reactivations).
> - SQLite (for tests) and SQL Server migrations will automatically apply safe column/table additions in `app.py` on application startup.
>
> **Access Restriction & Redirects**:
> - Super Admins will use the standard login screen. If `is_admin` is true, the user is redirected immediately to `/admin`.
> - Non-admin users are blocked from loading `/admin` by a routing guard and redirected to `/login` or `/workspace/default`.
>
> **Sensitive Data Warning**:
> - Super Admins can browse all saved collection requests and execution histories. To protect user privacy, a clear warning banner will be displayed in the collections view, and every instance of viewing request details or history is recorded immutably in the `admin_audit_log`.

---

## Design Review

### 2.1 Architecture Rationale
- We isolate administrative endpoints under a dedicated Flask blueprint (`admin_bp` in `backend/routes/admin_routes.py`) and service module (`backend/services/admin_service.py`). This prevents administrative logic from cluttering standard user flows and enforces clean authorization checks at the route entry point.
- The admin frontend is housed inside a separate React route `/admin` using a specialized layout component (`AdminDashboard.js`). This separates admin views from standard workspace rendering.

### 2.2 State Ownership
| State | Owner | Layer |
|---|---|---|
| Admin details (`is_admin`) | `AuthContext` | Global (App-wide) |
| Active Admin Tab | `AdminDashboard` | Feature-level (Admin panel) |
| Users / Workspaces list | `AdminDashboard` | Feature-level (Admin panel) |
| In-app Notifications | `TopBar` / Custom Hook | Global UI |

- Global authentication details (`is_admin`) are stored in `AuthContext` to protect routes.
- Individual dashboard sections (`AdminUsersTab`, `AdminWorkspacesTab`, `AdminAuditLogTab`) manage local search/sort/filter state using local React `useState`.

### 2.3 Service Ownership
- **Backend Service**: `backend/services/admin_service.py` houses all logic for listings, suspends, deletes, promotions, demotions, and audit logging.
- **Backend Routes**: `backend/routes/admin_routes.py` registers the blueprint.
- **Frontend Service**: `frontend/api-craft-app/src/services/adminService.js` wraps HTTP fetches for the `/api/admin/...` endpoints.

### 2.4 Testing Strategy
- **Backend integration tests** (`backend/tests/test_admin.py`):
  - Happy path for user management (list, suspend, reactivate, promote, demote, delete).
  - Happy path for workspace and collection listing and deletion.
  - Verification that non-admins hitting any admin route receive `403 Forbidden`.
  - Verification that suspended users cannot log in.
  - Audit logging coverage for actions.
- **Frontend smoke tests**:
  - `AdminDashboard.test.js` to assert it renders without crashing.

### 2.5 Scalability Concerns
- Deleting users or workspaces cascades deletion to collections, requests, and histories. We use SQLAlchemy cascade relationships to handle clean deletes, keeping database overhead low.
- Audit logs grow continuously. We include pagination query parameters on the audit logs endpoint.

---

## Open Questions

None.

---

## Proposed Changes

### Database Layer

#### [MODIFY] [user_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit%20API%20tester/backend/models/user_model.py)
* Add `is_admin = db.Column(db.Boolean, default=False, nullable=False)`
* Add `is_suspended = db.Column(db.Boolean, default=False, nullable=False)`
* Add relationships to new notification and log models.

#### [NEW] [audit_log_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/audit_log_model.py)
* Create `AdminAuditLog` model matching the requirements (admin_id, action, target_type, target_id, target_snapshot, created_at).

#### [NEW] [notification_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/notification_model.py)
* Create `UserNotification` model matching requirements (user_id, message, is_read, created_at).

#### [MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)
* Import new models.
* Register table/column check logic inside `create_app()` startup:
  * Safe-add columns `is_admin` and `is_suspended` to `users` table if missing.
  * Create `admin_audit_log` and `user_notifications` tables if missing.
  * Register `admin_bp` route blueprint.

---

### Backend Service Layer

#### [MODIFY] [auth_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/auth_service.py)
* In `login_user(username, password)`, check if the resolved user has `is_suspended == True`. If so, return failure tuple: `(None, "Your account has been suspended. Please contact the administrator.")`.
* Include `is_admin` field in successful login payload.

#### [NEW] [admin_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/admin_service.py)
Implement core functions with mandatory audit log writing:
* `get_all_users(admin_id)`
* `suspend_user(admin_id, target_user_id)`
* `reactivate_user(admin_id, target_user_id)`
* `delete_user(admin_id, target_user_id)`
* `promote_to_admin(admin_id, target_user_id)`
* `demote_from_admin(admin_id, target_user_id)`
* `get_all_workspaces(admin_id)`
* `delete_workspace_by_admin(admin_id, workspace_id)`
* `get_workspace_collections(admin_id, workspace_id)`
* `delete_collection_by_admin(admin_id, collection_id)`
* `log_sensitive_view(admin_id, workspace_id, details)`
* `get_audit_logs(admin_id, limit, offset)`
* `get_user_notifications(user_id)`
* `mark_notifications_read(user_id)`

---

### Backend Route Layer

#### [NEW] [admin_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/admin_routes.py)
Defines administrative endpoints with strict `@token_required` and verification of user admin privileges:
* `GET /api/admin/users`
* `POST /api/admin/users/<id>/suspend`
* `POST /api/admin/users/<id>/reactivate`
* `DELETE /api/admin/users/<id>`
* `POST /api/admin/users/<id>/promote`
* `POST /api/admin/users/<id>/demote`
* `GET /api/admin/workspaces`
* `DELETE /api/admin/workspaces/<id>`
* `GET /api/admin/workspaces/<id>/collections`
* `DELETE /api/admin/collections/<id>`
* `POST /api/admin/workspaces/<id>/log-view` (registers a log entry whenever an admin reads request details/history)
* `GET /api/admin/audit-logs`
* `GET /api/notifications` (for regular users)
* `POST /api/notifications/read` (for regular users)

---

### Frontend Service Layer

#### [NEW] [adminService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/adminService.js)
Define endpoints wrapping the HTTP calls:
* `getAdminUsers()`, `suspendUser()`, `reactivateUser()`, `deleteUser()`, `promoteUser()`, `demoteUser()`
* `getAdminWorkspaces()`, `deleteWorkspaceByAdmin()`, `getWorkspaceCollectionsByAdmin()`, `deleteCollectionByAdmin()`
* `logSensitiveView()`, `getAuditLogs()`
* `getUserNotifications()`, `markNotificationsRead()`

---

### Frontend Hook & State Layer

#### [MODIFY] [AuthContext.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/contexts/AuthContext.js)
* Store and expose `isAdmin` flag retrieved from standard user token login payload.

---

### Frontend UI Components

#### [NEW] [AdminDashboard.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/AdminDashboard.js)
#### [NEW] [AdminDashboard.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/AdminDashboard.css)
* Main page container for admins. Shares identical typography and table layout styling as the user dashboard.
* Sections: Users, Workspaces, Audit Log.

#### [NEW] [AdminUsersTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/AdminUsersTab.js)
* Table displaying users, accounts status (Active/Suspended), is_admin status.
* User actions: Suspend, Reactivate, Promote, Demote, Delete (with confirmation modal).

#### [NEW] [AdminWorkspacesTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/AdminWorkspacesTab.js)
* List of workspaces.
* Clicking into a workspace reveals nested collections, requests list, and execution history.
* Displays a clear privacy alert banner. Whenever requests or history are clicked, fires `logSensitiveView()`.
* Deletion buttons for workspaces and collections.

#### [NEW] [AdminAuditLogTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/AdminAuditLogTab.js)
* Displays reverse-sorted logs showing admin name, action timestamp, type, and snapshot details.

#### [NEW] [NotificationBell.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/NotificationBell.js)
#### [NEW] [NotificationBell.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/admin/NotificationBell.css)
* Topbar notification bell component rendering unread items count and a dropdown list of messages.

#### [MODIFY] [TopBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.js)
* Mount the `<NotificationBell>` component next to the workspace picker/logout controls.

#### [MODIFY] [Login.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Login.js)
* On successful login, if `is_admin` is true, navigate directly to `/admin`.
* Gracefully display account suspension error text if received from the login endpoint.

#### [MODIFY] [App.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/App.js)
* Add `AdminRoute` wrapper checks.
* Define route: `/admin` mapping to `<AdminDashboard />`.

---

## API Contract Changes

### `POST /api/auth/login`
* Response adds `is_admin`: `true` / `false` field.

### `GET /api/admin/users`
* Returns listing:
  ```json
  [
    {
      "id": 1,
      "username": "houdaifa",
      "email": "h@example.com",
      "is_admin": false,
      "is_suspended": false,
      "workspaces_count": 3
    }
  ]
  ```

---

## OpenAPI Spec Additions
Will append new admin path specifications:
* `/api/admin/users`
* `/api/admin/users/{id}/suspend`
* `/api/admin/users/{id}/reactivate`
* `/api/admin/users/{id}` (Delete)
* `/api/admin/users/{id}/promote`
* `/api/admin/users/{id}/demote`
* `/api/admin/workspaces`
* `/api/admin/workspaces/{id}`
* `/api/admin/workspaces/{workspace_id}/collections`
* `/api/admin/collections/{id}`
* `/api/admin/workspaces/{workspace_id}/log-view`
* `/api/admin/audit-logs`
* `/api/notifications`
* `/api/notifications/read`

---

## Rule Deviations
None.

---

## Verification Plan

### Automated Tests
* Run `pytest backend/tests/test_admin.py`
* Run frontend smoke tests.

### Manual Verification
1. Manually toggle `is_admin = 1` in SQL database on a test account.
2. Log in using that account. Confirm redirect lands on `/admin`.
3. Verify administrative interface tabs (Users, Workspaces, Audit Log) render and filter properly.
4. Suspend another user account. Verify that attempting to log in with the suspended user displays the suspension message.
5. Reactivate user account. Confirm log in succeeds.
6. Delete a workspace from workspaces tab. Confirm it is removed.
7. Verify all actions create new log records in the Audit Log view.
8. Log in as a regular user. Confirm receiving in-app suspension warnings and alerts via topbar notifications bell.
