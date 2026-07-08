# Implementation Plan — Inline Request Comments

This plan outlines the design and implementation of the **Workspace Chat & Contextual Annotations** feature in APICraft. It includes a centralized collaboration channel (Workspace Chat) that supports general workspace-level messages and request-specific contextual annotations.

---

## 1. Feature Summary
The "Inline Request Comments" feature introduces a single, unified collaboration channel within workspaces. Instead of isolated request comments, all discussions live in a chronological, centralized chat panel. Comments can be general, or bound to a specific request, tab, or key. Interactive badges allow users to navigate from chat directly to request elements, and hover elements on the request builder enable pre-binding context to new comments. Single-level nested replies are supported.

---

## 2. Design Review

### 2.1 Architecture Rationale
- **Single Chat Feed**: A single `comments` database table stores all comments (general, request-bound, tab-bound, and key-bound, as well as replies). This simplifies queries and ensures chronological integrity.
- **Polling Sync**: Frontend updates will use a short-polling loop (every 10 seconds) with window focus awareness. This avoids the complexity of WebSocket infrastructure while keeping sync fast during active collaboration.
- **Custom Event Coordination**: Interactive badge navigation from the chat sidebar will trigger a custom window event (`navigate-to-comment-context`). The `RequestBuilder` listens to this event to switch sub-tabs and trigger keyframe-based scrolling/glow animations. This keeps the components loosely coupled and prevents deep prop-drilling.
- **Key Renaming Tracking**: We leverage the frontend-generated row `id` (present in query params and headers states) to track key changes during request saves. By comparing old vs new parameters/headers in the service layer, we can accurately cascade key renames to bound comments.

### 2.2 State Ownership
- **Global Layer**: N/A (uses existing `AuthContext` for user identity and token).
- **Feature Layer (`useComments` hook)**:
  - `comments`: Loaded list of comment objects for the active workspace.
  - `isChatOpen`: Boolean state indicating sidebar visibility.
  - `activeFilter`: Filter state (e.g. `'all'`, `'request'`, or a specific element).
  - `draftBinding`: Context configuration `{ request_id, target_tab, target_key }` pre-bound when drafting comments.
- **Local UI Layer**:
  - `WorkspaceChat`: Local input content state, reply/edit input states.
  - `ParamsTab` / `HeadersTab` / `AuthorizationTab`: Hover states and inline count indicators.

### 2.3 Service Ownership
- **Backend Service (`backend/services/comment_service.py`)**: Handles CRUD logic, role check validations, deactivated user username resolution, and nested single-level replies formatting.
- **Backend Route (`backend/routes/comment_routes.py`)**: Thin orchestrator for comment endpoints.
- **Frontend Service (`frontend/api-craft-app/src/services/commentService.js`)**: Encapsulates network operations using `authFetch`.

### 2.4 Testing Strategy
- **Backend Integration Tests (`pytest`)**:
  - Validates endpoints under `backend/tests/test_comments.py`.
  - Scenarios covered:
    - Happy path: post general comment, post request/tab/key-bound comment, post reply.
    - Error path: reply nesting > 1 level (blocked), access comments in workspace user is not a member of (403), edit other's comment (403), delete other's comment as viewer/editor (403).
    - Boundary conditions: request cascade delete, param key rename update check.
- **Frontend Smoke Tests**:
  - `WorkspaceChat.test.js`: Smoke test verifying the WorkspaceChat component renders correctly under owner/viewer roles.

### 2.5 Scalability Concerns
- **Short-Polling Frequency**: Polling every 10 seconds per open tab can generate high traffic if many users leave tabs open. Mitigated by using a focus-aware loop: polling pauses when the window is blurred (`document.hasFocus() == false`).
- **Cascade Deletes**: Cascading deletions of requests/workspaces could hit query performance on large tables. SQLite/SQLServer foreign key constraints with `ondelete='CASCADE'` and SQLAlchemy relationship cascades are added to ensure database consistency.

---

## 3. Files to Create

### 3.1 Backend Files
1. **[comment_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/comment_model.py)** (~40 lines)
   - Defines the `Comment` SQLAlchemy model.
   - Schema fields: `id`, `workspace_id`, `user_id`, `content`, `parent_id`, `request_id`, `target_tab`, `target_key`, `created_at`, `updated_at`.
   - Setup relationship with cascade delete on requests.
2. **[comment_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/comment_service.py)** (~120 lines)
   - Business logic: get comments (retrieves parents and nests replies), create comment, update comment, delete comment.
   - Ownership and permission validations.
   - Deactivated user resolution.
3. **[comment_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/comment_routes.py)** (~80 lines)
   - Flask blueprint `comment_bp` exposing:
     - `GET /api/workspaces/<workspace_id>/comments`
     - `POST /api/workspaces/<workspace_id>/comments`
     - `PATCH /api/comments/<comment_id>`
     - `DELETE /api/comments/<comment_id>`
4. **[test_comments.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_comments.py)** (~150 lines)
   - Integration tests covering the comments REST API.

### 3.2 Frontend Files
1. **[commentService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/commentService.js)** (~40 lines)
   - Frontend API client for comment endpoints utilizing `authFetch`.
2. **[useComments.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/hooks/useComments.js)** (~80 lines)
   - State hook managing comments list, CRUD, short polling (focus-aware), active filters, and comment pre-binding drafts.
3. **[WorkspaceChat.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceChat.js)** (~140 lines)
   - Renders the slide-out chat feed panel from the right.
   - Renders message threads (replies), filter bars, bind dropdown selectors, edit/delete buttons.
4. **[WorkspaceChat.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceChat.css)** (~100 lines)
   - Premium glassmorphism design, scrollbars, hover states, and animations.
   - Adheres to `user-select: none; cursor: default;` for static elements.
5. **[WorkspaceChat.test.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceChat.test.js)** (~30 lines)
   - Smoke test for the chat sidebar.

---

## 4. Files to Modify

### 4.1 Backend Modifications
1. **[app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py)**
   - Import and register `comment_bp`.
   - Import `Comment` model to ensure schema auto-creation on boot.
2. **[request_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/request_service.py)**
   - Modify `save_request` to compare incoming `params` and `headers` against existing records by row ID.
   - If a row's key is renamed, execute an database update statement updating `comments.target_key` for that request and tab.

### 4.2 Frontend Modifications
1. **[MainPage.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPage.js)**
   - Integrate `useComments` hook.
   - Render `<WorkspaceChat>` sidebar alongside `MainPanel`.
   - Define a callback to handle click notifications on comment bubbles / `[+]` row buttons, linking back to the comments hook filter/draft bindings.
2. **[TopBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.js)** and **[TopBar.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.css)**
   - Add a premium message chat bubble toggle button next to the notification bell in the profile segment.
3. **[MainPanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPanel.js)**
   - Propagate comments list and click callbacks into `RequestBuilder`.
4. **[RequestBuilder.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestBuilder.js)**
   - Setup window event listener for `'navigate-to-comment-context'`.
   - On event trigger: switches sub-tabs to the targeted tab, scrolls the element into view, and highlights it with a temporary border glow.
   - Pass comments array and clicking callbacks to `RequestTabs` and active sub-tabs.
5. **[RequestTabs.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestTabs.js)**
   - Compute total comment counts for each request sub-tab (Params, Headers, Authorization, Body).
   - Render a small comment count badge adjacent to tab labels.
6. **[ParamsTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/ParamsTab.js)** and **[HeadersTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/HeadersTab.js)**
   - Map comments to compute inline key-specific comment counts.
   - Pass `commentCounts` and `onCommentClick` down to `KeyValueTable`.
7. **[KeyValueTable.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/shared/KeyValueTable.js)** and **[KeyValueTable.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/shared/KeyValueTable.css)**
   - Inject comment icon/button column next to keys.
   - If a row is hovered, show a small `[+]` button if it has no comments.
   - If it has comments, show a persistent count badge.
   - Assign unique IDs (`comment-target-<tab>-<key>`) to key input elements for targeted scrolling.
8. **[AuthorizationTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/AuthorizationTab.js)** and **[AuthorizationTab.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/AuthorizationTab.css)**
   - Support hover bubble `[+]` indicators and count badges next to the fields (Token, Username, Password).
   - Assign unique target IDs (`comment-target-auth-token`, etc.).
9. **[index.css](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/index.css)**
   - Define `@keyframes comment-glow` and `.comment-highlight-glow` transition styles.

---

## 5. API Contract Changes

### 5.1 GET `/api/workspaces/<workspace_id>/comments`
- **Method**: `GET`
- **Security**: JWT Bearer Token
- **Query Params**:
  - `request_id` (optional, integer)
- **Response Schemas**:
  - **200 OK**:
    ```json
    [
      {
        "id": 1,
        "workspace_id": 5,
        "user_id": 2,
        "username": "jane_doe",
        "content": "Should we change pagination defaults?",
        "parent_id": null,
        "request_id": 12,
        "request_name": "Get Users",
        "target_tab": "params",
        "target_key": "limit",
        "created_at": "2026-07-08T13:00:00Z",
        "updated_at": "2026-07-08T13:00:00Z",
        "replies": [
          {
            "id": 2,
            "workspace_id": 5,
            "user_id": 3,
            "username": "Deactivated User",
            "content": "Yes, make it 50.",
            "parent_id": 1,
            "request_id": null,
            "target_tab": null,
            "target_key": null,
            "created_at": "2026-07-08T13:05:00Z",
            "updated_at": "2026-07-08T13:05:00Z"
          }
        ]
      }
    ]
    ```
  - **401 Unauthorized**: Token missing or invalid.
  - **403 Forbidden**: User not a member of the workspace.
  - **404 Not Found**: Workspace not found.

### 5.2 POST `/api/workspaces/<workspace_id>/comments`
- **Method**: `POST`
- **Security**: JWT Bearer Token
- **Request Body**:
  ```json
  {
    "content": "This is a comment",
    "parent_id": 1, 
    "request_id": 12,
    "target_tab": "params",
    "target_key": "limit"
  }
  ```
- **Response Schemas**:
  - **201 Created**: Returns the saved comment dictionary.
  - **400 Bad Request**: Invalid body validation (e.g. infinite nesting, missing parent comment, mismatched workspaces).
  - **403 Forbidden**: User has no access to the workspace.

### 5.3 PATCH `/api/comments/<comment_id>`
- **Method**: `PATCH`
- **Security**: JWT Bearer Token
- **Request Body**:
  ```json
  {
    "content": "Edited comment content"
  }
  ```
- **Response Schemas**:
  - **200 OK**: Returns the updated comment dictionary.
  - **403 Forbidden**: Attempting to edit other's comment, or no longer in workspace.
  - **404 Not Found**: Comment not found.

### 5.4 DELETE `/api/comments/<comment_id>`
- **Method**: `DELETE`
- **Security**: JWT Bearer Token
- **Response Schemas**:
  - **200 OK**: `{"message": "Comment deleted"}`
  - **403 Forbidden**: No permission to delete (non-owners cannot delete other's comments).
  - **404 Not Found**: Comment not found.

---

## 6. OpenAPI Spec Additions
The following will be added to `backend/openapi.yaml`:
```yaml
  /api/workspaces/{workspace_id}/comments:
    get:
      summary: Get workspace comments
      security:
        - BearerAuth: []
      parameters:
        - name: workspace_id
          in: path
          required: true
          schema:
            type: integer
        - name: request_id
          in: query
          required: false
          schema:
            type: integer
      responses:
        '200':
          description: A list of comments
        '403':
          description: Access denied
    post:
      summary: Post a comment or reply
      security:
        - BearerAuth: []
      parameters:
        - name: workspace_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - content
              properties:
                content:
                  type: string
                parent_id:
                  type: integer
                request_id:
                  type: integer
                target_tab:
                  type: string
                target_key:
                  type: string
      responses:
        '201':
          description: Comment created
        '400':
          description: Invalid nesting or payload
        '403':
          description: Access denied
  /api/comments/{comment_id}:
    patch:
      summary: Edit a comment
      security:
        - BearerAuth: []
      parameters:
        - name: comment_id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - content
              properties:
                content:
                  type: string
      responses:
        '200':
          description: Comment updated
        '403':
          description: Unauthorized to edit
        '404':
          description: Not found
    delete:
      summary: Delete a comment
      security:
        - BearerAuth: []
      parameters:
        - name: comment_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Comment deleted
        '403':
          description: Unauthorized to delete
        '404':
          description: Not found
```

---

## 7. Rule Deviations
- None. All architectural constraints, file locations, state boundaries, styling limits, and testing tiers are strictly observed.

---

## 8. Verification Plan

### Automated Tests
- Run backend pytest tests:
  `pytest backend/tests/test_comments.py`
- Run frontend smoke test:
  `npm test src/components/workspace/WorkspaceChat.test.js`

### Manual Verification (Browser E2E)
1. **Chat Sidebar Slide-Out**: Click the toggle button in the TopBar; verify Workspace Chat slides open from the right.
2. **Posting a General Comment**: Write a message in the input at the bottom, ensure it appears chronologically in the chat window.
3. **Nesting a Reply**: Click 'Reply' under the posted comment. Type a reply and verify it is nested exactly one level deep. Verify no 'Reply' action exists on the child reply.
4. **Creating a Bound Annotation from Row**: Go to request parameters, hover on a row, click the `[+]` bubble. Verify Chat panel opens and shows the binder auto-filled. Type comments and post. Verify count badge appears on the row.
5. **Interactive Navigation Badge**: Click the context badge (`[Get Users > Params > limit]`) in the Chat feed. Verify:
   - Request switches to targeted request.
   - Targeted request shifts tabs to `Params`.
   - Key field scrolls into view and flashes an amber outline.
6. **Key Renaming Cascade**: Rename a query parameter key from `limit` to `pageSize` and click Save. Verify that the badge in the chat updates to `[Get Users > Params > pageSize]`.
7. **Viewer Security Boundary**: Log in as a viewer. Verify parameter input fields are read-only, but comments bubble `[+]` displays on hover, allowing comment addition. Verify backend throws error on PUT/PATCH requests.
8. **Deactivated User UI Check**: Remove a user from the workspace who previously commented. Verify their comment creator field displays "Deactivated User".
