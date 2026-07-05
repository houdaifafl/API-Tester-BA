# Walkthrough — Leave Workspace (Member Self-Removal)

This walkthrough documents the implementation and verification of the **Leave Workspace** feature, built on top of the existing Workspace Roles system.

---

## 1. Summary of Changes

Members (Editors and Viewers) can now voluntarily leave any workspace they joined via an invitation. Leaving immediately deletes their `WorkspaceMember` record, removes the workspace from their list, and navigates them to their next available workspace.

### 1.1 Backend Implementation
* **`workspace_service.py`**: Added `leave_workspace(workspace_id, user_id)` — validates that the caller is not the owner, finds their `WorkspaceMember` row, deletes it, and commits.
* **`workspace_routes.py`**: Added `DELETE /api/workspaces/<workspace_id>/leave` (JWT protected) — calls the service, returns 200 on success, 403 for owners, 404 if not a member.
* **`openapi.yaml`**: Documented the new endpoint with all response codes (200, 401, 403, 404).

### 1.2 Frontend Implementation
* **`workspaceService.js`**: Added `leaveWorkspace(workspaceId)` — calls `DELETE /api/workspaces/{id}/leave` via `authFetch`.
* **`WorkspaceDropdown.js`**: Added amber `FaSignOutAlt` Leave button next to each workspace where `is_owner === false`. Uses a two-click confirmation pattern (`leavingId` state) — first click shows a pulsing "Confirm?" label, second click executes the leave and calls `onWorkspaceDeleted`.
* **`WorkspaceDropdown.css`**: Added `.wsd-leave-btn` and `.wsd-leave-btn--confirm` styles — amber/orange color scheme with a pulsing keyframe animation on confirmation state.

---

## 2. Verification Results

### Tier 1 — Backend pytest Integration Tests
Added 6 new test cases under `TestLeaveWorkspace` in `backend/tests/test_workspaces.py`:

| Test | Scenario | Result |
|---|---|---|
| `test_editor_can_leave_workspace` | Happy path — Editor leaves | ✅ 200 |
| `test_viewer_can_leave_workspace` | Happy path — Viewer leaves | ✅ 200 |
| `test_owner_cannot_leave_workspace` | Error — Owner blocked | ✅ 403 |
| `test_non_member_leave_returns_404` | Error — Non-member | ✅ 404 |
| `test_workspace_inaccessible_after_leave` | Boundary — Access revoked | ✅ 403 |
| `test_missing_token_returns_401` | Error — No auth | ✅ 401 |

**Total: 156/156 tests pass.**

### Frontend Build
`npm run build` — **Compiled successfully. Zero warnings.**

---

## 3. UX Behaviour

- The **Leave** button (↩ icon) appears on hover next to shared workspaces in the workspace dropdown — only for members, never for owners.
- First click → button turns amber and shows "Confirm?" with a pulsing animation.
- Second click → `leaveWorkspace()` is called; the workspace disappears from the list and the app navigates to the next available workspace.
- Owners see no Leave button — only their existing red delete (🗑) button on non-default workspaces.
