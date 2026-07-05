# Implement Workspace-Level Roles and Permissions

This plan details the implementation of Workspace-Level Roles (Owner, Editor, Viewer) and the visual and functional authorization restrictions required for standard collaborative workspaces.

---

## User Review Required

> [!IMPORTANT]
> **Database Migration Cleanup**: All existing invitation records in the `invitations` table must be deleted during database migration/startup to ensure data integrity and avoid schema issues with the new `role` field.
>
> **Visual Indicator**: The frontend will render a visible "Read-only" badge icon next to the workspace selection name if the user's role is `viewer`.
>
> **UI Actions Restrictions & User Alerts**:
> * All buttons and options (e.g. "+" add buttons, Save buttons, context menus, Settings, Invite members, and delete buttons) will remain visible in the UI for all roles to keep the interface identical.
> * If a user tries to perform a restricted action (e.g. Viewer clicks Save or "+", or Editor/Viewer clicks Invite members or Settings/Delete Workspace), the app will intercept the click and display a popup alert (Meldung) informing them of the restriction.
> * If the user encounters a `403 Forbidden` on loading a workspace (e.g. by typing a forbidden workspace ID in the browser URL), the app will show the popup alert and immediately revert/navigate the user back to their active/default workspace rather than loading a blank "Access denied" page at the forbidden URL.

---

## Workspace Role Authorization Edge Cases (Triggering Alert Popup)

For any user (specifically Viewers trying to bypass UI restrictions, or non-owners trying to perform admin tasks), the following actions are checked at the database/service layer and will return a `403 Forbidden` response, triggering the global frontend popup alert:

1. **Adding a Collection**: Trying to call `POST /api/workspaces/{workspace_id}/collections` on a workspace where the user is a Viewer.
2. **Renaming a Collection**: Trying to call `PATCH /api/collections/{collection_id}` where the user is a Viewer.
3. **Deleting a Collection**: Trying to call `DELETE /api/collections/{collection_id}` where the user is a Viewer.
4. **Creating a Request**: Trying to call `POST /api/collections/{collection_id}/requests` where the user is a Viewer.
5. **Saving a Request Configuration**: Trying to call `PATCH /api/requests/{request_id}` to save method, URL, params, headers, or body where the user is a Viewer.
6. **Renaming a Request**: Trying to call `PATCH /api/requests/{request_id}` to change the label where the user is a Viewer.
7. **Deleting a Request**: Trying to call `DELETE /api/requests/{request_id}` where the user is a Viewer.
8. **Sending Workspace Invitations**: Trying to call `POST /api/workspaces/{workspace_id}/invitations` where the user is a Viewer or Editor (only Owners are authorized).
9. **Deleting a Workspace**: Trying to call `DELETE /api/workspaces/{workspace_id}` where the user is not the Owner (Editors/Viewers cannot delete workspaces).
10. **Accessing a Forbidden Workspace**: Trying to load `GET /api/workspaces/{workspace_id}` for a workspace the user is not a member or owner of. In this specific case, the alert popup is displayed, and the frontend automatically reverts the browser URL back to the user's default active workspace.

---

## Open Questions

None. The user has confirmed the requirements regarding legacy invitation deletion and visual badges.

---

## Proposed Changes

### Database Layer

#### [MODIFY] [invitation_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/invitation_model.py)
* Add `role = db.Column(db.String(20), nullable=False, default='viewer')` column.

#### [MODIFY] [workspace_member_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/workspace_member_model.py)
* Add `role = db.Column(db.String(20), nullable=False, default='viewer')` column.

#### [MODIFY] [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)
* Add database startup logic inside `create_app()`:
  * Purge all pre-existing records in the `invitations` table before applying schema additions.
  * Auto-patch SQLite / SQL Server schemas to add the `role` column to `invitations` and `workspace_members`.

---

### Backend Service Layer

#### [MODIFY] [invitation_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/invitation_service.py)
* Update `create_invitation(workspace_id, inviter_id, invitee_username, role='viewer')`: Validate that `role` is either `'editor'` or `'viewer'`. Write the role value.
* Update `get_pending_invitations(user_id)`: Include the invitation `role` in the returned payload.
* Update `accept_invitation(invitation_id, user_id)`: Extract `role` from invitation and add to the created `WorkspaceMember` instance.

#### [MODIFY] [workspace_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/workspace_service.py)
* Update `get_workspace_by_id(workspace_id, user_id)`: Query `WorkspaceMember` for members, or return `'owner'` if the user matches `workspace.user_id`. Include `role` in the returned workspace dict.

---

### Backend Route Layer

#### [MODIFY] [invitation_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/invitation_routes.py)
* Update `create_invitation_route(workspace_id)`: Parse `role` from JSON request body, default to `'viewer'`, and validate value before invoking service.

#### [MODIFY] [collection_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/collection_routes.py)
* Add permission check: Deny collection write/edit actions (`POST`, `PATCH`, `DELETE`) with `403 Forbidden` if user is a viewer.

#### [MODIFY] [request_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/request_routes.py)
* Add permission check: Deny request write/edit/rename actions (`POST`, `PATCH`, `DELETE`) with `403 Forbidden` if user is a viewer.

---

### Frontend Service Layer

#### [MODIFY] [api.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/api.js)
* Update `authFetch` to intercept any backend response with a status code of `403`. Dispatch a custom `'show-unauthorized-alert'` window event containing the error message to trigger the application's Alert Modal.

#### [MODIFY] [invitationService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/invitationService.js)
* Update `inviteUserToWorkspace(workspaceId, username, role)`: Send `role` inside the payload.

---

### Frontend Hook & State Layer

#### [MODIFY] [useWorkspace.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/hooks/useWorkspace.js)
* Retrieve and expose `workspaceRole` from active workspace metadata.
* Update `getWorkspaceById` catch block: if error status is `403`, trigger fallback workspace list loading, and automatically navigate/revert the user back to their default or first available workspace.

---

### Frontend UI Components

#### [NEW] [AlertModal.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/shared/AlertModal.js)
#### [NEW] [AlertModal.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/shared/AlertModal.css)
* Build a custom modal React component styled with dark glassmorphism styling, a warning triangle icon, clear error messages, and a dismiss button.

#### [MODIFY] [MainPage.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPage.js)
* Setup a listener for the `'show-unauthorized-alert'` custom event on mount, store the message in an active state, and render the custom `<AlertModal>` when the state is active.

#### [MODIFY] [InviteModal.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/InviteModal.js)
* Add role selection select/dropdown (options: "Editor", "Viewer") default value "editor".

#### [MODIFY] [WorkspaceDropdown.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceDropdown.js)
* Keep "Invite members" and "Settings" buttons always visible.
* Keep workspace delete buttons always visible.
* If a user with `workspaceRole !== 'owner'` clicks "Invite members", "Settings", or deletes a workspace, intercept and trigger the custom `'show-unauthorized-alert'` event.

#### [MODIFY] [Sidebar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/Sidebar.js)
* Keep collection and request "+" add buttons always visible.
* Keep context menus (Rename/Delete) always visible.
* If `workspaceRole === 'viewer'`:
  * Intercept collection/request creation clicks, renaming triggers, or context menu deletes, and trigger the custom `'show-unauthorized-alert'` event with a descriptive warning message.
  * Render the "Read-only" badge next to the workspace selection name.

#### [MODIFY] [TopBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.js)
* Render "Read-only" badge next to workspace selector name.

#### [MODIFY] [RequestBuilder.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestBuilder.js)
* Keep "Save" button always visible.
* If `workspaceRole === 'viewer'` and the user clicks "Save", intercept and trigger the custom `'show-unauthorized-alert'` event, and block the save action.

---

## API Contract Changes

### `POST /api/workspaces/<workspace_id>/invitations`
* Request Body:
  ```json
  {
    "username": "invitee_username",
    "role": "editor" // or "viewer"
  }
  ```
* Response (201 Created):
  ```json
  {
    "message": "Invitation sent successfully",
    "invitation_id": 4
  }
  ```
* Response (400 Bad Request):
  ```json
  {
    "error": "Invalid role specified"
  }
  ```

---

## OpenAPI Spec Additions
Modify [openapi.yaml](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/openapi.yaml):
* Update `/api/workspaces/{workspace_id}/invitations` path definitions:
  * Add optional `role` schema parameter (string, enum: `['editor', 'viewer']`, default `'viewer'`) inside requestBody properties.

---

## Rule Deviations
None.

---

## Verification Plan

### Automated Tests
* Run backend tests: `pytest backend/tests/` (extend tests in `test_invitations.py`, `test_workspaces.py` to cover viewer role restrictions).
* Run frontend smoke tests: `npm test` inside `frontend/api-craft-app`.

### Manual Verification
1. Log in as User A. Create workspace. Verify role is `'owner'`.
2. Invite User B as `'viewer'`.
3. Log in as User B, accept invitation. Switch to workspace.
4. Verify User B sees "Read-only" badge, cannot save requests, cannot add collections.
5. Verify User B can execute requests successfully.
6. Verify API prevents raw HTTP updates (e.g. POST collections) from User B.
7. Invite User C as `'editor'`. Verify User C can edit requests but cannot invite new members.
