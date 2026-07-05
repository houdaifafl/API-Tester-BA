# APICraft Requirement Document: Super Admin

This document outlines the functional and non-functional requirements for implementing a **Super Admin** role in APICraft. Any implementation plan or code generation must follow these instructions.

---

## 1. Feature Overview

APICraft currently operates with a flat user model augmented by workspace-level roles (Owner, Editor, Viewer). This feature adds a global **Super Admin** role that transcends all workspace boundaries and provides a dedicated administrative dashboard for platform-level management.

The Super Admin has full visibility and control over all users, workspaces, and collections across the entire platform — but every action they take is logged and, where appropriate, communicated to the affected user.

---

## 2. Super Admin Identity & Bootstrapping

### 2.1 Admin Flag in the Database
- A new boolean column `is_admin` (default `False`, non-nullable) is added to the `users` table.
- The **first Super Admin** is designated by manually setting `is_admin = True` directly in the database for one existing user account.
- Subsequent Super Admins are promoted through the Admin UI by an existing Super Admin.
- A Super Admin can also **demote** another Super Admin (but cannot demote themselves).

### 2.2 Admin Login Flow
- Super Admins log in through the **same login page** as regular users.
- After successful login, the backend detects `is_admin = True` and returns an `is_admin: true` flag alongside the JWT token and workspace data.
- The frontend detects this flag and **redirects the admin directly to `/admin`** instead of `/workspace/:id`.
- A Super Admin **never** lands on the normal workspace dashboard.

### 2.3 Admin Session Isolation
- A Super Admin cannot switch to the normal workspace view.
- A regular user cannot access `/admin` — any attempt redirects to `/login`.

---

## 3. Admin Dashboard UI

### 3.1 Separate Route
- The admin dashboard lives at `/admin`.
- It is a fully separate page, isolated from the workspace UI.
- Protected by an `AdminRoute` wrapper in `App.js` (analogous to `ProtectedRoute` but requires `is_admin: true`).

### 3.2 Dashboard Layout
The dashboard has a **top navigation bar** with four main sections:

| Section | Icon | Description |
|---|---|---|
| **Users** | 👥 | List, search, view, manage all registered users |
| **Workspaces** | 🗂️ | List, search, view, manage all workspaces |
| **Collections** | 📁 | Browse collections inside any workspace |
| **Audit Log** | 📋 | Chronological log of all admin actions |

### 3.3 Visual Style
- The admin dashboard must share the same design language, styling conventions, and visual theme as the user's workspace UI.
- Use the same clean color palettes, typography, table borders, request details layouts, and shared component designs (such as key-value grids and modals) to ensure a cohesive look-and-feel across the application.
- Tables must support sorting and keyword search/filtering.

---

## 4. User Management

### 4.1 User List View
The admin sees a paginated, searchable table of all registered users with the following columns:
- Username
- Email
- Join date
- Number of workspaces owned
- Account status (`Active` / `Suspended`)
- Is Admin badge (if the user is also a Super Admin)

### 4.2 User Detail View
Clicking a user opens a detail panel showing:
- Full profile (username, email, join date)
- List of workspaces they own (name, collection count, member count)
- List of workspaces they are a member of (name, their role)
- Account status

### 4.3 User Actions
The following actions are available from the user detail view:

| Action | Behaviour |
|---|---|
| **Suspend** | Sets `is_suspended = True` on the user. The user cannot log in while suspended. A suspension notification is sent in-app. |
| **Re-activate** | Sets `is_suspended = False`. The user can log in again. A re-activation notification is sent in-app. |
| **Delete** | Permanently deletes the user and cascades: all their owned workspaces, collections, requests, history entries, and invitations are deleted. A deletion notification email is logged (in-app channel). Requires a confirmation modal. |
| **Promote to Admin** | Sets `is_admin = True`. The user will be redirected to `/admin` on next login. |
| **Demote from Admin** | Sets `is_admin = False`. Only available if the target is an admin. Not available for self. |

### 4.4 Suspended User Behaviour
- When a suspended user attempts to log in, the backend returns `403 Forbidden` with the message: `"Your account has been suspended. Please contact the administrator."`
- The login page displays this message clearly.

---

## 5. Workspace Management

### 5.1 Workspace List View
A searchable, sortable table of all workspaces across all users:
- Workspace name
- Owner username
- Number of members
- Number of collections
- Creation date

### 5.2 Workspace Actions
| Action | Behaviour |
|---|---|
| **View** | Opens the workspace detail view (see 5.3) |
| **Delete** | Permanently deletes the workspace and all its collections, requests, and history. Requires confirmation modal. |

### 5.3 Workspace Detail View
- Workspace name, owner, members list (with roles), creation date
- Collection list (see Section 6)

---

## 6. Collection & Request Management

### 6.1 Collection List View (inside a Workspace)
- All collections in the selected workspace, with their request count.
- The admin can **view** and **delete** individual collections.

### 6.2 Request & History Access
- The admin can drill into a collection to view all saved request configurations (method, URL, params, headers, body, auth).
- The admin can view the workspace's request execution history entries.

> [!CAUTION]
> **Privacy Notice**: Request configurations and history entries may contain sensitive information (API keys in headers, auth credentials, production URLs). Access to this data is logged in the audit trail. This must be clearly disclosed in the admin UI with a visible warning banner.

---

## 7. Audit Log

### 7.1 Logged Events
Every admin action generates an audit log entry:

| Event | Logged Fields |
|---|---|
| User suspended | admin_id, target_user_id, timestamp |
| User re-activated | admin_id, target_user_id, timestamp |
| User deleted | admin_id, target_user_id, target_username (snapshot), timestamp |
| User promoted to admin | admin_id, target_user_id, timestamp |
| User demoted from admin | admin_id, target_user_id, timestamp |
| Workspace deleted | admin_id, workspace_id, workspace_name (snapshot), timestamp |
| Collection deleted | admin_id, collection_id, collection_name (snapshot), workspace_id, timestamp |
| Sensitive data viewed | admin_id, workspace_id, collection_id (if applicable), timestamp |

### 7.2 Audit Log UI
- Displayed as a chronological reverse-sorted table in the **Audit Log** section of the admin dashboard.
- Searchable/filterable by admin username, action type, and date range.
- Entries are **immutable** — no admin can delete audit log records.

### 7.3 Data Model
New table: `admin_audit_log`
- `id` (PK, Integer)
- `admin_id` (FK → users.id, nullable=False)
- `action` (String, e.g. `'suspend_user'`, `'delete_workspace'`)
- `target_type` (String, e.g. `'user'`, `'workspace'`, `'collection'`)
- `target_id` (Integer, nullable — may be null if target was deleted)
- `target_snapshot` (JSON, nullable — stores name/username at time of action)
- `created_at` (DateTime, UTC)

---

## 8. In-App User Notifications

When an admin suspends, re-activates, or deletes a user account, the affected user must receive an in-app notification:

- **Suspension**: `"Your account has been suspended by an administrator."`
- **Re-activation**: `"Your account has been re-activated. You can log in again."`
- **Deletion**: Logged only (user no longer exists to receive it, but snapshot is kept in audit log)

### 8.1 Notification Model
New table: `user_notifications`
- `id` (PK, Integer)
- `user_id` (FK → users.id, nullable=False)
- `message` (String)
- `is_read` (Boolean, default False)
- `created_at` (DateTime, UTC)

### 8.2 Notification UI
- A bell icon (🔔) in the workspace TopBar shows unread count.
- Clicking opens a notification dropdown listing unread messages.
- Clicking a notification marks it as read.

---

## 9. Privacy Principles

| Principle | Implementation |
|---|---|
| **Least-privilege visibility** | Admin access to request content and history is explicitly logged, not silent |
| **Audit immutability** | Audit log cannot be edited or deleted by anyone, including admins |
| **Action confirmation** | Destructive actions (delete user, delete workspace) require a typed confirmation or modal |
| **Transparency to users** | Users are notified of suspension and re-activation |
| **Admin isolation** | Admins cannot impersonate users or make requests on their behalf |
| **No silent access** | Every admin page view of sensitive request/history data generates an audit entry |

---

## 10. Out of Scope (for this version)
- Admin cannot reset user passwords directly (user must use standard auth flow)
- Admin cannot edit or modify saved requests or history entries (read-only for content)
- Admin cannot reassign workspace ownership
- No public-facing audit log (users cannot see the admin audit trail)
- No multi-tenancy / organization-level admin roles
