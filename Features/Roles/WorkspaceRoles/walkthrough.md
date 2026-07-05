# Walkthrough — Workspace-Level Roles

This walkthrough documents the implementation and verification details of the **Workspace-Level Roles** feature.

---

## 1. Summary of Changes

We implemented a robust system of workspace roles (**Owner**, **Editor**, and **Viewer**) with full database, service, route, and frontend UI synchronization.

### 1.1 Backend Implementation
*   **Database Schema**: Added the `role` column to the `invitations` and `workspace_members` tables.Purged legacy invitation records and backfilled existing members to `'viewer'` dynamically on startup.
*   **Services**:
    *   `invitation_service.py`: Restructured invitation checks so only the workspace owner can send invites, and stored/serialized chosen roles.
    *   `workspace_service.py`: Injected active user roles into workspace metadata and added `check_user_write_access` to gate mutations.
    *   `collection_service.py` / `request_service.py`: Enforced write-permission gates on collections and requests for Viewers, returning `403 Forbidden` status. Removed deprecated `Model.query.get(id)` syntax.
*   **Routes**: Modified invitation, collection, and request blueprints to validate role payloads and return proper `403` status codes.

### 1.2 Frontend Implementation
*   **Global Interceptor**: Configured `authFetch` in `api.js` to catch any `403` status code globally and trigger a user-facing warning alert.
*   **Custom Hooks**: Exposed `workspaceRole` in `useWorkspace.js`.
*   **UI Layout & Permission Checks**:
    *   `InviteModal.js`: Added a dropdown to select either `'Editor'` or `'Viewer'` when inviting members.
    *   `Sidebar.js`: Hides adding collections, requests, and context menus for Viewers. Renders a visible lock badge indicator.
    *   `TopBar.js`: Displays a `🔒 Read-only` badge next to the active workspace name if the user is a Viewer.
    *   `WorkspaceDropdown.js`: Hides the 'Invite members' and 'Settings' buttons for non-owners, and restricts deleting workspaces to owners.
    *   `RequestBuilder.js` / `MainPanel.js`: Hides the request 'Save' button for Viewers.

---

## 2. Verification Results

We verified the code using the **three-tier testing strategy**.

### Tier 1 — Backend pytest Integration Tests
*   Added 4 new test cases under `backend/tests/test_invitations.py` verifying:
    *   Restricting invitations to workspace owners (blocking members like Editors from inviting).
    *   Returning bad request status for invalid invitation roles.
    *   Creating database membership rows with the matching role on invitation acceptance.
*   Ran the backend test suite: **150/150 tests passed successfully**.

### Tier 3 — Browser-Based End-to-End Verification
We verified the complete flow using a browser subagent executing signup, workspace creation, invitations, acceptance, dashboard layouts, and custom popup alert modals.

#### E2E Verification Media (Happy Path):

````carousel
![Viewer Collab Space Read-Only](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/viewer_collab_space_readonly_1783269388045.png)
<!-- slide -->
![Editor Collab Space Editable](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/editor_collab_space_editable_1783269457558.png)
<!-- slide -->
![Editor Custom Collection Created](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/editor_write_permission_success_1783269492418.png)
<!-- slide -->
![E2E Video Session](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/workspace_roles_e2e_1783268859147.webp)
````

#### E2E Verification Media (Custom App Modals — Edge Cases):

````carousel
![Custom Add Collection Modal](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/collections_alert_modal_1783273004054.png)
<!-- slide -->
![Custom Invite Members Modal](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/invite_alert_modal_1783273018023.png)
<!-- slide -->
![Custom Save Request Modal](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/save_alert_modal_1783273033737.png)
<!-- slide -->
![E2E Recording — All Forbidden Action Modals](C:/Users/hlanj/.gemini/antigravity-ide/brain/6bda4e92-1556-45ba-983b-df00d2ecc363/custom_popups_e2e_1783272955847.webp)
````

*   **Viewer Visual Layout**: Displays the lock badge next to the collection header and active workspace header. All "+" buttons, context menu triggers, and request Save buttons remain visible. Clicking any of them intercepts the event and pops up our custom application-styled `AlertModal` overlay (e.g. `"Action forbidden: Viewers cannot create collections."`, `"Viewers cannot save request changes."`).
*   **Editor Visual Layout**: Exposes full collection and request write capabilities. Re-ordering, creating, and renaming items function as normal. Clicking the visible `"Invite members"` or `"Settings"` dropdown options intercepts the action and displays the custom styled `AlertModal` overlay: `"Action forbidden: Only workspace owners can invite members."` / `"Only workspace owners can modify settings."`.
*   **Workspace Re-routing**: Attempting to load an unauthorized workspace triggers the custom warning modal and immediately re-routes/reverts the browser back to their active workspace dashboard rather than showing a blank error screen.
