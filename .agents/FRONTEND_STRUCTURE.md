# APICraft — Frontend Structure Map

This document provides a living map of the APICraft frontend application (`frontend/api-craft-app`). It details the directory layout, routing structure, state management architecture, component inventory, custom hooks, service layer, and critical data flows.

---

## 1. Directory Tree & File Overview

The React frontend follows a structured domain-based layout under `src/`:

```
src/
├── App.js                     # Root router, protected route wrapper
├── index.js                   # Application entry point
├── index.css                  # Global CSS styles
├── constants.js               # Global constants (e.g., HTTP method colors)
│
├── contexts/
│   └── AuthContext.js         # Global Auth Context & Hook
│
├── hooks/
│   ├── useWorkspace.js        # Workspace selection, validation, loading hook
│   ├── useCollections.js      # Collections/Requests CRUD state management hook
│   └── useWorkspaceTabs.js    # Workspace tab and state cache hook
│
├── services/
│   ├── api.js                 # API base configuration (BASE_URL)
│   ├── authService.js         # Authentication API client
│   ├── workspaceService.js    # Workspace API client
│   ├── collectionService.js   # Collection API client
│   └── requestService.js      # HTTP Request execution/management client
│
└── components/
    ├── auth/                  # Authentication pages
    │   ├── Login.js / .css    # Login page
    │   └── Signin.js / .css   # Registration page
    │
    ├── shared/                # Reusable presentation components
    │   └── KeyValueTable.js / .css
    │
    ├── workspace/             # Layout & Workspace coordination
    │   ├── MainPage.js / .css         # God/Layout coordinator
    │   ├── MainPanel.js               # Tab-switching panel
    │   ├── OverviewPanel.js / .css    # Workspace welcome/documentation tab
    │   ├── Sidebar.js / .css          # Workspace navigation pane
    │   ├── TopBar.js / .css           # Top header and open tab switcher
    │   ├── WorkspaceDropdown.js/.css  # Workspace selector dropdown
    │   ├── RequestContextMenu.js/.css # Context menu for requests/collections
    │   └── SignOutModal.js / .css     # Sign-out confirmation modal
    │
    └── request/               # Request composition & builder tabs
        ├── RequestBuilder.js / .css   # Request builder container
        ├── RequestBar.js              # Address bar and HTTP method selector
        ├── RequestTabs.js             # Sub-tab navigator (Params, Body, etc.)
        ├── DocsTab.js                 # Textarea for request documentation
        ├── ParamsTab.js / .css        # Query parameter manager
        ├── AuthorizationTab.js / .css # Auth type and credentials manager
        ├── HeadersTab.js              # Headers manager (implicitly shares ParamsTab.css)
        ├── BodyTab.js / .css          # Body format (raw, urlencoded, formdata) manager
        └── ResponsePanel.js           # Executed request response panel
```

---

## 2. Routing Map

All routing is defined in [App.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/App.js):

* **`/login`** -> [Login.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Login.js): Authenticates existing user.
* **`/signup`** -> [Signin.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Signin.js): Signs up a new user.
* **`/workspace/:workspaceId`** -> [ProtectedRoute](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/App.js#L7-L11) -> [MainPage.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPage.js): Renders workspace dashboard.
* **`*`** (Fallback) -> Redirects to `/login`.

---

## 3. Three-Layer State Model

### 3.1 Global Layer (User Identity)
* **Mechanism**: React Context API via `AuthProvider` and `useAuth()` in [AuthContext.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/contexts/AuthContext.js).
* **State Values**:
  * `user`: Object containing `userId`, `email`, and `username` retrieved from/persisted in `localStorage`.
* **Actions**:
  * `setUser(userData)`: Updates user identity state.
  * `logout()`: Clears `localStorage` and resets `user` to null values.

### 3.2 Feature-Level Layer (Workspace & Tabs)
* **Mechanism**: Handled in [MainPage.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPage.js) and coordinated via the custom hook [useWorkspaceTabs.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/hooks/useWorkspaceTabs.js).
* **MainPage State**:
  * `workspaces` (array): User's available workspaces.
  * `activeWorkspace` (object): Metadata of current workspace.
  * `collections` (array): Nested collections and requests in current workspace.
  * `sidebarWidth` (number): Width of resizing sidebar.
* **useWorkspaceTabs Hook State**:
  * `openTabs` (array): Ordered list of open tab descriptors: `{ id, type, label, method, requestId, collectionName }`.
  * `activeTabId` (string): Active tab ID.
  * `requestStates` (useRef object): Transient/unsaved inputs for opened request parameters/headers/body indexed by `requestId`.
  * `responseHeights` (useRef object): Resizable height settings for each request's response panel indexed by `requestId`.
  * `workspaceTabsCache` (useRef object): Caches the open tabs, active tab ID, and transient request states per workspace ID so that switching workspaces restores layout state.

### 3.3 Local UI Layer
* **Mechanism**: Component-level `useState` and `useRef`.
* **Examples**:
  * [Sidebar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/Sidebar.js): `collapsedCols` (Set of collapsed collections), `searchQuery` (filtering input), `menuState` (context menu anchor/rect), `renaming` (target request/collection ID and value).
  * [TopBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.js): `dropdownOpen` (workspace dropdown toggled), `accountOpen` (profile menu toggled), `confirmOpen` (logout modal toggled).
  * [AuthorizationTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/AuthorizationTab.js): `dropdownOpen` (Auth dropdown select toggled).

---

## 4. Component Inventory

### 4.1 Auth Components (`src/components/auth/`)
* **[Login.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Login.js)**
  * *Responsibility*: User authentication form.
  * *Interactions*: Invokes `login()` from `authService.js`, sets global auth context, redirects to workspace.
* **[Signin.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/auth/Signin.js)**
  * *Responsibility*: User registration form.
  * *Interactions*: Invokes `signup()` from `authService.js`, logs user in on success.

### 4.2 Workspace Coordination Components (`src/components/workspace/`)
* **[MainPage.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPage.js)**
  * *Responsibility*: God layout component. Performs API load operations, validates workspace ownership, binds sidebar callbacks to service operations, coordinates tabs.
* **[Sidebar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/Sidebar.js)**
  * *Responsibility*: Renders collection explorer tree and global actions (history, search, add collection). Handles double-click context menu renaming.
* **[TopBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/TopBar.js)**
  * *Responsibility*: Workspace switcher trigger, tab bar list, and user account menu toggle.
* **[WorkspaceDropdown.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/WorkspaceDropdown.js)**
  * *Responsibility*: Overlay list displaying available workspaces, with support for adding and deleting custom workspaces.
* **[MainPanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/MainPanel.js)**
  * *Responsibility*: Switches center screen between the `OverviewPanel` (welcome/docs screen) and `RequestBuilder` based on current tab type.
* **[OverviewPanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/OverviewPanel.js)**
  * *Responsibility*: General workspace welcome landing page. Features a two-tab view: `Docs` and `Updates`.
* **[RequestContextMenu.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/RequestContextMenu.js)**
  * *Responsibility*: Absolute-positioned overlay for collection/request actions (Rename, Delete).
* **[SignOutModal.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/workspace/SignOutModal.js)**
  * *Responsibility*: Basic dialog modal checking sign-out intent.

### 4.3 Request Composition Components (`src/components/request/`)
* **[RequestBuilder.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestBuilder.js)**
  * *Responsibility*: Main request configuration layout container. Manages execution loading states, maps/restores sub-tab states, and triggers background save/execution calls.
* **[RequestBar.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestBar.js)**
  * *Responsibility*: Displays HTTP method toggle dropdown, URL address text input field, and execution "Send" button.
* **[RequestTabs.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/RequestTabs.js)**
  * *Responsibility*: Sub-navigation tabs: Docs, Params, Authorization, Headers, Body.
* **[DocsTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/DocsTab.js)**
  * *Responsibility*: Simple description editor text container.
* **[ParamsTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/ParamsTab.js)**
  * *Responsibility*: Query parameter manager. Populates grid rows dynamically and bubbles changes back.
* **[AuthorizationTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/AuthorizationTab.js)**
  * *Responsibility*: Supports Bearer token and Basic auth (Username/Password) input composition.
* **[HeadersTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/HeadersTab.js)**
  * *Responsibility*: Renders Header input list using shared `KeyValueTable` component.
* **[BodyTab.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/BodyTab.js)**
  * *Responsibility*: Renders request body editor based on bodyType radio input selection (`none`, `form-data`, `x-www-form-urlencoded`, `raw`).
* **[ResponsePanel.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/request/ResponsePanel.js)**
  * *Responsibility*: Renders request execution metadata (HTTP code, time) and response body text output. Includes custom click-and-drag height resizing.

### 4.4 Shared Components (`src/components/shared/`)
* **[KeyValueTable.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/components/shared/KeyValueTable.js)**
  * *Responsibility*: Tabular grid mapping columns (Key, Value, Description, Delete action) for query parameter, header, and URL-encoded body parameters. Can dynamically toggle dropdown column for multipart file inputs.

---

## 5. Custom Hooks

### 5.1 `useWorkspaceTabs(workspaceIdParam)`
Coordinates and retains active layout state for request and documentation tabs within and across workspaces.

* **Key Internal Refs**:
  * `workspaceTabsCache`: Caches workspace layout data structure:
    ```javascript
    {
      [workspaceId]: {
        openTabs: [...],
        activeTabId: "...",
        requestStates: { [reqId]: { url, params, headers, body, auth } },
        responseHeights: { [reqId]: height }
      }
    }
    ```
  * `requestStates`: Key-value storage holding the current form states for edited requests. Kept in a ref so edits do not trigger full tab content re-renders until saved or executed.
* **Exposed API**:
  * `openTabs`: Active list of open tab configurations.
  * `activeTabId`: Currently focused tab.
  * `handleRequestOpen(request)`: Adds request to tabs list, creates default transient state structure, and focuses it.
  * `handleTabChange(tabId)`: Sets active focus tab.
  * `handleTabClose(tabId)`: Safely discards tab and purges height and state cache entries.
  * `updateTabMethod`, `updateTabLabel`, `updateTabCollectionName`, `removeTabsByRequestIds`: Workspace sidebar callback wrappers ensuring synchronization between tree changes and open tabs.

### 5.2 `useWorkspace()`
Coordinates workspaces list loading, active workspace ownership validation, creation/deletion routing redirects, and error handling states.

* **Exposed API**:
  * `workspaces`: Array of workspaces owned by the user.
  * `activeWorkspace`: Currently active workspace metadata.
  * `workspaceLoading`: Boolean indicating if workspace validation is in progress.
  * `workspaceError`: Error string ('invalid', 'not_found', 'forbidden') or null.
  * `workspaceIdParam`: The current workspace ID parameter from the URL.
  * `handleSwitch(workspace)`: Switches the current route to target workspace.
  * `handleWorkspaceCreated(workspace)`: Adds a newly created workspace and routes to it.
  * `handleWorkspaceDeleted(workspaceId)`: Deletes workspace from local list, falling back to default or next workspace if current is deleted.

### 5.3 `useCollections({ activeWorkspaceId, handleRequestOpen, ... })`
Encapsulates CRUD operations and state synchronization for collections and requests under the active workspace.

* **Exposed API**:
  * `collections`: Nested array of collections and requests in the active workspace.
  * `handleSaveRequest(requestId, data)`: Persists request updates to the database and syncs local collections state.
  * `handleRequestMethodChange(requestId, newMethod)`: Synchronizes request method updates with database and active tabs.
  * `handleRequestRename(requestId, newName)`: Renames request inside collection state and active tabs.
  * `handleRequestDelete(requestId)`: Deletes request and removes related open tabs.
  * `handleRequestAdd(collectionId)`: Seeds and opens a new request under target collection.
  * `handleCollectionAdd()`: Adds a new collection under the active workspace.
  * `handleCollectionRename(collectionId, newName)`: Renames collection and cascades tab collectionName metadata.
  * `handleCollectionDelete(collectionId)`: Deletes collection, cascading request deletion and removing their tabs.

---

## 6. Service Layer Map (`src/services/`)

All HTTP communication utilizes standard `fetch` syntax. Base configuration is established via [api.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/api.js):
```javascript
const BASE_URL = 'http://localhost:5000';
export default BASE_URL;
```

### 6.1 Services Listing
* **[authService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/authService.js)**:
  * `login(username, password)` -> `POST /api/auth/login`
  * `signup(username, firstName, email, password)` -> `POST /api/auth/signup`
* **[workspaceService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/workspaceService.js)**:
  * `getWorkspaces(userId)` -> `GET /api/workspaces?user_id={id}`
  * `createWorkspace(userId, name)` -> `POST /api/workspaces`
  * `getWorkspaceById(workspaceId, userId)` -> `GET /api/workspaces/{id}?user_id={id}` (attaches `.status` code to thrown `Error` for handling 403 vs 404 client rendering).
  * `deleteWorkspace(workspaceId, userId)` -> `DELETE /api/workspaces/{id}?user_id={id}`
* **[collectionService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/collectionService.js)**:
  * `getCollections(workspaceId)` -> `GET /api/workspaces/{id}/collections`
  * `addCollection(workspaceId)` -> `POST /api/workspaces/{id}/collections`
  * `renameCollection(collectionId, name)` -> `PATCH /api/collections/{id}`
  * `deleteCollection(collectionId)` -> `DELETE /api/collections/{id}`
* **[requestService.js](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/frontend/api-craft-app/src/services/requestService.js)**:
  * `createRequest(collectionId)` -> `POST /api/collections/{id}/requests`
  * `renameRequest(requestId, name)` -> `PATCH /api/requests/{id}`
  * `updateRequestMethod(requestId, method)` -> `PATCH /api/requests/{id}`
  * `saveRequest(requestId, payload)` -> `PATCH /api/requests/{id}`
  * `deleteRequest(requestId)` -> `DELETE /api/requests/{id}`
  * `executeRequest(payload)` -> `POST /api/execute` (sends method, URL, formatted parameters/headers/body to backend proxy agent). Note: throws raw error dictionary instead of standard `Error` instances.

---

## 7. Key Data & Control Flows

### 7.1 Workspace Navigation & Loading Flow
1. URL changes to `/workspace/:workspaceId`.
2. `MainPage` triggers authentication checks.
3. Ownership and access are checked via `getWorkspaceById(workspaceIdParam, userId)`.
   * **Success**: Workspace metadata loads, then `getCollections(workspaceId)` is executed to populate the sidebar tree.
   * **Failure (403/404)**: Displays localized error screen overlay instead of dashboard.
4. Hook `useWorkspaceTabs` triggers workspace swap:
   * Saves current workspace's tabs state, active tab index, and form variables to cache.
   * Restores target workspace's tabs state and cached variables, or falls back to welcome default.

### 7.2 Request Execution Flow
1. User clicks **"Send"** button on `RequestBar`.
2. `RequestBuilder` coordinates parsing calculations:
   * Maps param list to query string dictionary.
   * Merges auth credentials (Basic username/password or Bearer token) directly into headers configuration.
   * Formats body object based on type (`form-data`, `urlencoded`, `raw`).
3. Invokes `executeRequest(payload)` in `requestService.js`.
4. Renders execution status and parsed payload result in `ResponsePanel`. Updates transient request state.

---

## 8. Frontend CSS & Styling Conventions

* **Styling Frameworks**: Plain CSS is used for all workspace layouts. Bootstrap 5 is restricted exclusively to authentication forms (`Login.css`, `Signin.css`).
* **Co-location**: CSS files are located in the same directory alongside their JS React components, using identical PascalCase names.
* **Colors**: Color constants for HTTP methods (GET, POST, etc.) are imported from `src/constants.js` (`METHOD_COLORS`) and applied inline.
* **Layout Mechanics**: Handles custom drag-to-resize columns (Sidebar width) and rows (Response panel height) by tracking global document mouse event listeners (`mousemove`, `mouseup`) initialized from mouse-down events.
