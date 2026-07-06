# Requirement Document: Unified Workspace Chat & Contextual Annotations

This document details the requirements and functional specifications for the **Workspace Chat & Contextual Annotations** feature in APICraft.

---

## 1. Feature Overview
The goal is to provide a single, unified collaboration channel within a workspace. Instead of comments being hidden inside specific requests, discussions happen in a centralized **Workspace Chat** panel. Messages in this chat can either be general workspace-level discussions or **contextually bound** to a specific request, tab, or field.

---

## 2. Core Functional Requirements

### 2.1 Central Workspace Chat Panel
* **Location**: Accessible via a collapsible sidebar panel or a main tab in the workspace view.
* **Flow**: Displays a chronological list of messages/threads.
* **Types of Messages**:
  1. **General Chat**: Plain text messages about workspace collaboration (not bound to any request).
  2. **Context-Bound Comments**: Messages created from, or linked to, a specific API request, tab, or parameter field.

### 2.2 Contextual Binding & Annotations
* **Binding Targets**: A comment can be bound to:
  * A specific **Request** (e.g. `"GET /users"`)
  * A specific **Request Tab** (e.g. `Headers`, `Params`, `Body`, `Auth`)
  * A specific **Parameter Key** (e.g. a query parameter key `limit` or header key `X-Api-Key`)
* **Creating a Bound Comment**:
  * **From the Chat Panel**: A dropdown allows the user to select an existing request and optionally choose a tab and input field to bind the comment.
  * **From the Request Builder**: Next to every parameter row, header row, and authorization field, hover states will display a small comment bubble icon `[+]`. Clicking it opens the workspace chat panel, automatically drafting a comment with the context pre-bound to that field.

### 2.3 Interactive Navigation & Highlighting
* **Navigating from Chat**:
  * Bound messages display a visible context badge (e.g., `[Get Users > Params > limit]`).
  * Clicking the badge automatically:
    1. Selects the target request in the sidebar.
    2. Switches the request panel to the target tab (e.g. `Params`).
    3. Scrolls to and highlights the target input field with a temporary visual outline (e.g., a glowing amber border).
* **Viewing Comments from the Request Builder**:
  * If a parameter, header, or tab has active comments, a persistent speech bubble badge (with a comment count) displays next to it.
  * Clicking the badge opens the Workspace Chat panel and filters it to show only comments bound to that specific element.

### 2.4 Discussion Feed with Direct Replies
* **Direct Replies (Single-Level Nesting)**: The chat panel displays comments in a chronological feed. Users can click "Reply" on any main message, which creates a child reply nested exactly one level deep. Nested child comments cannot have further nested replies (no infinite threading) to keep the interaction and database clean.

---

## 3. Roles & Permissions Boundary
Permissions align with APICraft's workspace-level roles:

| Action | Workspace Owner | Workspace Editor | Workspace Viewer |
|--------|-----------------|------------------|------------------|
| Post General / Bound Comment | Yes | Yes | Yes |
| Reply to a Message | Yes | Yes | Yes |
| Delete Own Comments / Replies | Yes | Yes | Yes |
| Delete Other Users' Comments | Yes | No | No |
| Edit Own Comments / Replies | Yes | Yes | Yes |

---

## 4. Conceptual Data Model

### 4.1 Schema Definition
We will store all comments in a single unified table with optional nullable fields for contextual binding and parent-child hierarchy:

* **`comments` Table**:
  * `id` (Integer, Primary Key)
  * `workspace_id` (Integer, Foreign Key to `Workspace`, nullable=False)
  * `user_id` (Integer, Foreign Key to `User`, nullable=False)
  * `content` (Text, nullable=False)
  * `parent_id` (Integer, Foreign Key to `Comment.id`, nullable=True) — *For single-level thread replies*
  * `request_id` (Integer, Foreign Key to `Request`, nullable=True) — *Bound request*
  * `target_tab` (String, nullable=True) — *Allowed values: `params`, `headers`, `body`, `auth`*
  * `target_key` (String, nullable=True) — *The key name of the parameter/header annotated*
  * `created_at` (DateTime, auto-populate)
  * `updated_at` (DateTime, auto-update)

### 4.2 Cascading Behaviors
* **Deleted Requests**: If an editor deletes a request, all comments bound to that `request_id` must cascade delete automatically.
* **Leaving Workspace**: If a user leaves the workspace or is removed, their comments remain visible to preserve conversation logs, but the creator field displays as `"Deactivated User"`.

---

## 5. User Interface (UI) Design Notes
* **Workspace Chat Sidebar**:
  * Slides out from the right side of the screen when clicked.
  * Contains a filter bar: `[All]`, `[Bound to Current Request]`.
* **Hover Annotations**:
  * A lightweight `[+]` button appears adjacent to parameter rows when hovering over the row.
* **Glow/Highlight Effect**:
  * A custom CSS keyframe animation should animate a soft highlight on a target input field when clicked from the chat, making it easy to find in complex requests.

---

## 6. Architectural & Synchronisation Decisions

### 6.1 Key Renaming Handling (Option A)
* **Behavior**: If a user renames a query parameter or header key (e.g. `userId` to `user_id`), any comment currently bound to `userId` must have its `target_key` automatically updated to `user_id` upon saving the request. 
* **Database Impact**: The request update service layer will check for key changes and issue an `UPDATE` on the `comments` table matching `request_id`, `target_tab`, and the old key name, updating `target_key` to the new key name.

### 6.2 Live Collaboration Updates (Option A)
* **Synchronisation**: The React frontend will execute a short-polling loop using `setInterval` (e.g., every 10 seconds) to fetch updated comments for the currently active workspace.
* **UX Optimizations**: A polling manager hook will skip requests when the window is out of focus to conserve server resources and network traffic.

### 6.3 Viewer UX & Security Boundaries (Option A)
* **Visual Hover Badging**: For users with the `viewer` role, the parameter input fields and header inputs are disabled/read-only. However, when a Viewer hovers over a parameter or header row, the comment bubble `[+]` button will still appear.
* **Interaction**: Clicking this button will open the comment panel to write a comment bound to this parameter.
* **Strict Read-Only Parameter Constraints**:
  * Viewers are strictly prohibited from editing keys, values, descriptions, checkboxes, or deleting rows.
  * The frontend input fields must remain `disabled={true}` or `readOnly={true}`.
  * The comment interaction must not trigger any form submit or request save event that could overwrite database request definitions.
  * Backend routing layers must continue to reject any `PUT`/`PATCH` request modifications from users with the `viewer` role, regardless of frontend actions.
