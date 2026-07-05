# APICraft Requirement Document: Workspace-Level Roles & Collaborative Permissions

This document outlines the requirements and functional specifications for implementing Workspace-Level Roles in the APICraft application. Any implementation plan or code generation must follow these instructions.

---

## 1. Feature Overview
The goal is to transition APICraft from a flat authorization model to a Role-Based Access Control (RBAC) model at the workspace level. Workspaces will support three roles:
1. **Workspace Owner** (Creator of the workspace)
2. **Workspace Editor** (Read-write collaborator)
3. **Workspace Viewer** (Read-only consumer)

When a workspace owner invites a new user, they must be able to select the role (`editor` or `viewer`) that the invited user will receive once they accept.

---

## 2. Core Requirements

### 2.1 Workspace Ownership
* **Automatic Assignment**: The user who creates a new workspace must automatically be designated as its **Owner**.
* **Implicit Ownership**: The system must check the `Workspace.user_id` to resolve ownership.

### 2.2 Invitation Flow with Role Selection
* **UI Selector**: When inviting a member to a workspace, the user interface must display a dropdown selection with two options:
  * **Editor** (Default or selected)
  * **Viewer**
* **Invitation Database Storage**: The system must store the selected role associated with the invitation in the database.
* **Acceptance Logic**: When a user accepts an invitation, they must be added to the `WorkspaceMember` table with the role specified in their invitation.

### 2.3 Role Definitions & Permissions

#### A. Workspace Owner (Full Access)
* **Scope**: The user whose ID matches the workspace's `user_id`.
* **Capabilities**:
  * Manage workspace settings (rename, delete workspace).
  * Invite new users and choose their workspace role.
  * Modify existing members' roles or revoke memberships.
  * Create, modify, and delete collections and requests.
  * View and execute all requests.

#### B. Workspace Editor (Read-Write Access)
* **Scope**: A user listed in the `workspace_members` table with the role `'editor'`.
* **Capabilities**:
  * Create, modify, and delete collections and requests.
  * View and execute all requests.
  * Manage workspace execution history (clear history).
* **Restrictions**:
  * Cannot rename or delete the workspace.
  * Cannot invite, edit, or remove workspace members.

#### C. Workspace Viewer (Read-Only Access)
* **Scope**: A user listed in the `workspace_members` table with the role `'viewer'`.
* **Capabilities**:
  * View collections, requests, and request layouts.
  * Execute (run) requests and view response results.
* **Restrictions**:
  * Cannot edit, rename, or delete requests or collections.
  * Cannot create new collections or requests.
  * The "Save" actions/buttons on the request panel must be disabled or hidden.
  * Cannot invite, edit, or remove workspace members.
  * Cannot manage or delete the workspace.

---

## 3. Data Model Requirements

### 3.1 `invitations` Table Update
* Add a `role` column:
  * **Type**: String (Length: 20)
  * **Constraints**: `nullable=False`, default value `'viewer'`.
  * **Allowed values**: `'editor'`, `'viewer'`.

### 3.2 `workspace_members` Table Update
* Add a `role` column:
  * **Type**: String (Length: 20)
  * **Constraints**: `nullable=False`, default value `'viewer'`.
  * **Allowed values**: `'editor'`, `'viewer'`.

### 3.3 Legacy Invitation Purge
* **Migration Cleanup**: All pre-existing invitations in the `invitations` database table must be deleted during migration to ensure schema consistency and prevent missing roles on older records.

---

## 4. API Contract Requirements

### 4.1 Create Invitation
* **Endpoint**: `POST /api/workspaces/<workspace_id>/invitations`
* **Request Body Schema**:
  ```json
  {
    "email": "invitee@example.com",
    "role": "editor" // Or "viewer"
  }
  ```
* **Validation**:
  * Verify that the requesting user is the workspace owner.
  * Verify that `role` is either `"editor"` or `"viewer"`.
  * Create the invitation record containing the selected role.

### 4.2 Accept Invitation
* **Endpoint**: `POST /api/invitations/<invitation_id>/accept`
* **Behavior**:
  * Read the `role` from the accepted invitation.
  * Add the user as a `WorkspaceMember` with that specific `role`.

---

## 5. UI/UX Functional Requirements

### 5.1 Invitation Modal
* Include a role selector field (dropdown or toggle) next to the email input field.
* Options must clearly list `"Editor"` and `"Viewer"`.

### 5.2 Conditional Rendering based on Role
* **If current user is Viewer**:
  * Display a visible "Read-only" badge icon next to the workspace selection name in the interface.
  * Disable or hide the "+" (Add Collection) buttons in the Sidebar.
  * Hide or disable the "Save" and "Save As" buttons in the request panel.
  * Disable drag-and-drop ordering of collections/requests.
  * Hide the "Workspace Members / Invite" interface, or display members in a read-only list.
* **If current user is Editor**:
  * Keep request-editing and creation buttons active.
  * Hide buttons for managing workspace settings or inviting new members.

### 5.3 Error Alerts for Unauthorized Operations
* If any user (Owner, Editor, or Viewer) attempts an operation that is rejected by the backend with a `403 Forbidden` status code, the application must display a clear, user-facing alert/message (e.g. "Action forbidden: You do not have permission to perform this operation" or "Action forbidden: Viewers cannot modify collections or requests.").
