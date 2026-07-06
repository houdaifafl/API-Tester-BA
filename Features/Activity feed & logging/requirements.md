# Requirement Document: Workspace Activity Feed & Audit Logging

This document outlines the requirements and specifications for tracking and viewing collaborative activities within an APICraft workspace.

---

## 1. Feature Overview
A collaborative workspace requires transparency so team members know who modified what request, when collections were restructured, and who entered or left the workspace. 
The **Workspace Activity Feed & Audit Logging** feature provides a chronological ledger of changes.

---

## 2. Core Functional Requirements

### 2.1 Tracked Activity Categories
The backend must capture and log the following events within a workspace:

1.  **Workspace Settings**:
    *   Renaming the workspace.
2.  **Collaborator Management**:
    *   Inviting a user (log includes invitee email and invited role).
    *   Revoking/cancelling an invitation.
    *   Accepting an invitation (joining the workspace).
    *   Modifying a member's role (e.g., editor to viewer).
    *   Removing a member or a member leaving.
3.  **Collection Modifications**:
    *   Creating a collection.
    *   Renaming a collection.
    *   Deleting a collection.
    *   Updating collection-level authorization.
4.  **Request Modifications**:
    *   Creating a request.
    *   Renaming a request.
    *   Updating request fields (method, URL, headers, params, body, auth).
    *   Deleting a request.
5.  **Request Executions (Run Logging)**:
    *   Executing any request (log includes endpoint method, URL, status code, response time).

### 2.2 Log Visibility & Access Control Boundaries
To preserve administrative security and workspace governance, we enforce distinct visibility tiers:

*   **Workspace Owners & Editors**:
    *   Have full access to all logged activities (including collaborator changes, setting changes, requests, and runs).
*   **Workspace Viewers**:
    *   Have **restricted access** to logs.
    *   *Visible logs*: Collection actions, request creations/edits, and request run logs.
    *   *Hidden logs*: Collaborator management logs (invitations, role upgrades, member removals) and workspace settings/renaming actions to prevent leak of user management flow.

---

## 3. Data Representation & Snapshot Diffing

### 3.1 Workspace Activity Log Table Schema
We will create a new model dedicated to workspace logs:

*   **`workspace_activities` Table**:
    *   `id` (Integer, Primary Key)
    *   `workspace_id` (Integer, Foreign Key to `Workspace`, nullable=False)
    *   `user_id` (Integer, Foreign Key to `User`, nullable=False) — *The person who performed the action*
    *   `event_category` (String, e.g., `workspace`, `membership`, `collection`, `request`, `execution`)
    *   `action` (String, e.g., `create`, `rename`, `update`, `delete`, `invite`, `join`, `leave`, `role_change`, `execute`)
    *   `target_type` (String, e.g., `request`, `collection`, `member`, `settings`)
    *   `target_name` (String, nullable=False) — *Cached name of request/collection/user for display consistency if deleted*
    *   `target_id` (Integer, nullable=True) — *ID of entity, if it still exists*
    *   `before_state` (JSON, nullable=True) — *Snapshot of modified columns before change*
    *   `after_state` (JSON, nullable=True) — *Snapshot of modified columns after change*
    *   `created_at` (DateTime, default=datetime.utcnow)

### 3.2 Payload Diffing Structure
*   For **Update** operations, `before_state` and `after_state` must only store fields that were modified.
    *   *Example (URL change)*:
        *   `before_state`: `{"url": "http://old-url.com"}`
        *   `after_state`: `{"url": "https://new-url.com"}`
*   For **Execution** logs, `after_state` stores runtime indicators:
    *   `after_state`: `{"status_code": 200, "response_time_ms": 145}`

---

## 4. User Interface (UI) Design Notes

### 4.1 Chronological Activity Feed
*   **Location**: Rendered as a dedicated tab (e.g., `Activity Log`) on the Workspace Overview Panel.
*   **Format**: A vertical feed showing user actions, timestamps, and an expandable detail toggler:
    *   👤 **Jane Doe** updated request **"Get Users"** - *10 minutes ago* `[Show Diffs]`
    *   👤 **Bob** executed `GET` **"Get Users"** (Status: `200 OK`, 142ms) - *2 hours ago*
*   **Diff Drawer / Visual Diff Viewer**:
    *   Clicking `[Show Diffs]` expands the log entry to show color-coded changed lines (red deletion block for `before_state` fields and green insertion block for `after_state` fields).

---

## 5. Credentials & Sensitive Data Scrubbing

### 5.1 Redaction Strategy
*   Before database persistence, both the frontend payload validation and the backend service layers must scan fields for credentials.
*   **Header & Param Sanitization**: Any keys in headers or parameters that match the following patterns (case-insensitive) must have their values replaced with `"[REDACTED]"` inside `before_state` and `after_state` blobs:
    *   `authorization` / `bearer`
    *   `cookie` / `set-cookie`
    *   `x-api-key` / `api_key` / `apikey`
    *   `token` / `access_token`
*   **Body Sanitization**: If the request body contains a JSON dictionary, search for fields named `password`, `secret`, `token`, `password_hash` and replace their values with `"[REDACTED]"`.
*   **Auth Fields**: The `auth` JSON payload must have its password or key tokens redacted entirely.

