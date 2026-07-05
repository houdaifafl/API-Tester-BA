# Implement Leave Workspace (Member Self-Removal)

A member (Editor or Viewer) who accepted a workspace invitation must be able to voluntarily leave that workspace at any time. Leaving removes their `WorkspaceMember` record and revokes all access to that workspace immediately.

---

## User Review Required

> [!IMPORTANT]
> **Owner cannot leave**: The workspace owner (`Workspace.user_id`) must not be able to leave their own workspace — only delete it. The backend must enforce this.
>
> **Immediate Effect**: Once a member leaves, the frontend must remove the workspace from their list and navigate them to their next available workspace.
>
> **UI Placement**: The "Leave workspace" action should be visible inside the `WorkspaceDropdown` for non-owners (Editor and Viewer), displayed next to the workspace entry in the workspace list — distinct from the existing delete (🗑) button shown to owners.

---

## Design Review

### 2.1 Architecture Rationale
A new `DELETE /api/workspaces/<workspace_id>/leave` endpoint is the cleanest fit. It acts on the calling user's own membership row — no resource ID needed other than the workspace itself (already in the URL). This keeps the route thin and the service focused.

The route lives in the existing `workspace_bp` blueprint because leaving is a workspace-level membership operation. No new blueprint is needed.

### 2.2 State Ownership
| State | Owner | Layer |
|---|---|---|
| `workspaces` list | `useWorkspace` hook | Feature-level |
| Navigation after leave | `useWorkspace.handleWorkspaceDeleted` | Feature-level |
| Leave confirmation state | `WorkspaceDropdown` | Local UI |

`handleWorkspaceDeleted` already handles removing a workspace from the local list and navigating to the fallback. We reuse it on the frontend after a successful leave.

### 2.3 Service Ownership
- **Backend**: New `leave_workspace(workspace_id, user_id)` function in `workspace_service.py`. Finds and deletes the calling user's `WorkspaceMember` row. Returns error if the user is the owner or not a member.
- **Frontend**: New `leaveWorkspace(workspaceId)` function in `workspaceService.js` calling `DELETE /api/workspaces/{id}/leave`.

### 2.4 Testing Strategy
- **Happy path**: Editor leaves workspace → 200, membership row deleted.
- **Error path**: Owner tries to leave → 403 Forbidden.
- **Error path**: Non-member tries to leave → 404 Not Found.
- **Frontend**: Smoke test that `WorkspaceDropdown` renders the leave button for non-owners.

### 2.5 Scalability Concerns
None significant. The delete is a single-row operation on `workspace_members` by `(workspace_id, user_id)` index. No cascades.

---

## Open Questions
None.

---

## Proposed Changes

### Backend Service Layer

#### [MODIFY] [workspace_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/workspace_service.py)
* Add `leave_workspace(workspace_id, user_id)`:
  * Fetch the workspace. If the calling user is the owner (`workspace.user_id == user_id`), return error: owners cannot leave.
  * Query `WorkspaceMember` for `(workspace_id, user_id)`. If not found, return 404 error.
  * Delete the membership row and commit.

---

### Backend Route Layer

#### [MODIFY] [workspace_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/workspace_routes.py)
* Add `DELETE /api/workspaces/<workspace_id>/leave` (JWT protected):
  * Call `leave_workspace(workspace_id, user_id)`.
  * Return 200 on success, 403 if owner, 404 if not a member.

---

### Backend OpenAPI

#### [MODIFY] [openapi.yaml](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/openapi.yaml)
* Add entry for `DELETE /api/workspaces/{workspace_id}/leave` with 200, 403, 404 responses.

---

### Frontend Service Layer

#### [MODIFY] [workspaceService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/workspaceService.js)
* Add `leaveWorkspace(workspaceId)` → `DELETE /api/workspaces/{id}/leave` (via `authFetch`, JWT protected).

---

### Frontend UI Components

#### [MODIFY] [WorkspaceDropdown.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceDropdown.js)
* For each workspace in the list where `ws.is_owner === false`, show a **"Leave"** button (e.g. `FaSignOutAlt` icon) next to the workspace name — distinct from the delete (🗑) button shown to owners.
* On click, show a confirmation prompt using our custom `AlertModal` or a simple inline confirmation state, then call `leaveWorkspace(ws.id)` and invoke `onWorkspaceDeleted(ws.id)` on success.

#### [MODIFY] [WorkspaceDropdown.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceDropdown.css)
* Style the leave button (`.wsd-leave-btn`) visually distinct from the delete button — use a muted warning color (e.g. amber/orange) rather than red.

---

## API Contract Changes

### `DELETE /api/workspaces/<workspace_id>/leave`
* **Auth**: Bearer JWT token required.
* **Response (200 OK)**:
  ```json
  { "message": "You have left the workspace." }
  ```
* **Response (403 Forbidden)**:
  ```json
  { "error": "Workspace owners cannot leave their own workspace." }
  ```
* **Response (404 Not Found)**:
  ```json
  { "error": "Membership not found." }
  ```

---

## OpenAPI Spec Additions

```yaml
/api/workspaces/{workspace_id}/leave:
  delete:
    summary: Leave a workspace as a member
    tags: [Workspaces]
    security:
      - BearerAuth: []
    parameters:
      - in: path
        name: workspace_id
        required: true
        schema:
          type: integer
    responses:
      '200':
        description: Successfully left workspace
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      '403':
        description: Owner cannot leave their own workspace
      '404':
        description: Membership not found
```

---

## Rule Deviations
None.

---

## Verification Plan

### Automated Tests
* Add tests in `backend/tests/test_workspaces.py`:
  * `TestLeaveWorkspace` class with happy path, owner-forbidden, and non-member-404 cases.
* Run: `pytest backend/tests/`

### Manual Verification
1. Log in as `editor_user`, open the workspace dropdown.
2. Verify a **"Leave"** button appears next to the shared workspace.
3. Click **"Leave"** and confirm. The workspace disappears from the list.
4. Verify `editor_user` can no longer access that workspace (403).
5. Log in as `owner_user` and verify the Leave button does NOT appear for their own workspaces.
