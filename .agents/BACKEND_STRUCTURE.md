# APICraft — Backend Structure Map

This document provides a living map of the APICraft backend application (`backend/`). It details the factory layout, routing structure, database models, service layers, integration tests, and configuration details.

---

## 1. Application Factory Pattern

The backend utilizes the Flask application factory pattern. The server entry point is managed inside [app.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/app.py):

* **`create_app()` Function**:
  * Initializes the Flask application.
  * Configures the Database URI (currently points to SQL Server LocalDB/Express: `mssql+pyodbc://@MSI\\SQLEXPRESS01/API_tester?driver=ODBC+Driver+17+for+SQL+Server`).
  * Enables CORS (cross-origin resource sharing) for wildcard origins.
  * Binds and initializes the Flask-SQLAlchemy `db` context.
  * Hot-patches SQL Server database instances automatically during startup (e.g., adding `auth NVARCHAR(MAX) NULL` to the `requests` table if missing).
  * Registers all blueprints.
* **Blueprints Registered**:
  * `api_client_bp` -> Handles proxied HTTP request execution.
  * `collection_bp` -> Handles CRUD actions for collection organization.
  * `auth_bp` -> Handles user login and signup actions.
  * `workspace_bp` -> Handles workspace dashboard operations.
  * `request_bp` -> Handles CRUD actions for saved request configurations.
  * `history_bp` -> Handles request execution history logs.

---

## 2. Database Schema & ORM Models

All database models reside inside `backend/models/` and extend from SQLAlchemy's base [base.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/base.py) declarative mapping class:

```
                  ┌──────────────┐
                  │     User     │
                  └──────┬───────┘
                         │ 1
                         │
                         │ *
                  ┌──────▼───────┐
                  │  Workspace   │
                  └──────┬───────┘
                         │ 1
                         │
                         │ * (nullable FK)
                  ┌──────▼───────┐
                  │  Collection  │
                  └──────┬───────┘
                         │ 1
                         │
                         │ *
                  ┌──────▼───────┐
                  │   Request    │
                  └──────────────┘
```

### 2.1 Model Registry (`backend/models/`)
* **[user_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/user_model.py) (`User` model)**:
  * Table: `users`
  * Columns: `id` (PK, Integer), `username` (Unique, String), `first_name` (String), `email` (Unique, String), `password` (String, bcrypt hash).
  * Relationships: `workspaces` (one-to-many relationship mapping to `Workspace` model via `owner` backref), `memberships` (`WorkspaceMember` back_populates), `sent_invitations` / `received_invitations` (`Invitation` back_populates).
* **[workspace_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/workspace_model.py) (`Workspace` model)**:
  * Table: `workspaces`
  * Columns: `id` (PK, Integer), `name` (String), `user_id` (FK to `users.id`, nullable=False), `is_default` (Boolean, defaults to False).
  * Relationships: `collections` (one-to-many relationship mapping to `Collection` model via `workspace` backref; configured with cascade delete), `history_entries` (back_populates), `memberships` (back_populates), `invitations` (back_populates).
* **[workspace_member_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/workspace_member_model.py) (`WorkspaceMember` model)**:
  * Table: `workspace_members`
  * Columns: `id` (PK, Integer), `workspace_id` (FK to `workspaces.id`, nullable=False), `user_id` (FK to `users.id`, nullable=False), `role` (String, default='viewer'), `joined_at` (DateTime).
  * Relationships: `workspace` (back_populates), `user` (back_populates).
* **[invitation_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/invitation_model.py) (`Invitation` model)**:
  * Table: `invitations`
  * Columns: `id` (PK, Integer), `workspace_id` (FK to `workspaces.id`, nullable=False), `inviter_id` (FK to `users.id`, nullable=False), `invitee_id` (FK to `users.id`, nullable=False), `status` (String, default='pending'), `role` (String, default='viewer'), `created_at` (DateTime).
  * Relationships: `workspace` (back_populates), `inviter` (back_populates), `invitee` (back_populates).
* **[collection_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/collection_model.py) (`Collection` model)**:
  * Table: `collections`
  * Columns: `id` (PK, Integer), `name` (String), `workspace_id` (FK to `workspaces.id`, nullable=True — *known violation*), `is_default` (Boolean, defaults to False).
  * Relationships: `requests` (one-to-many relationship mapping to `Request` model via `collection` backref; configured with cascade delete).
* **[request_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/request_model.py) (`Request` model)**:
  * Table: `requests`
  * Columns: `id` (PK, Integer), `name` (String), `method` (String, nullable=False), `url` (String, nullable=False), `params` (JSON), `headers` (JSON), `body` (JSON), `auth` (JSON), `collection_id` (FK to `collections.id`, nullable=False).
* **[history_model.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/models/history_model.py) (`History` model)**:
  * Table: `history`
  * Columns: `id` (PK, Integer), `workspace_id` (FK to `workspaces.id`, nullable=False), `method` (String, nullable=False), `url` (String, nullable=False), `params` (JSON), `headers` (JSON), `body` (JSON), `auth` (JSON), `status` (Integer), `response_time` (Float), `data` (JSON), `created_at` (DateTime).
  * Relationships: `workspace` (many-to-one relationship mapping to `Workspace` model via `history` back_populates).

---

## 3. Blueprint-per-Domain Routing Map

Routes are thin orchestrators that digest JSON requests, delegate logic to services, and return JSON payloads.

| Blueprint | HTTP Method | Route Path | Service Delegation | Success | Error Status |
|---|---|---|---|---|---|
| **Auth** | `POST` | `/api/auth/signup` | `signup_user()` | 201 | 400 (missing fields), 409 (conflict) |
| | `POST` | `/api/auth/login` | `login_user()`, `get_user_workspaces()` | 200 | 400 (missing fields), 401 (invalid auth) |
| **Workspace**| `GET` | `/api/workspaces` (JWT) | `get_user_workspaces()` | 200 | 401 (unauthorized) |
| | `POST` | `/api/workspaces` (JWT) | `create_workspace()` | 201 | 400 (missing name), 401 (unauthorized) |
| | `GET` | `/api/workspaces/<workspace_id>` (JWT) | `get_workspace_by_id()` | 200 | 400 (invalid ID), 401 (unauthorized), 403 (forbidden), 404 (not found) |
| | `DELETE`| `/api/workspaces/<workspace_id>` (JWT) | `delete_workspace()` | 200 | 401 (unauthorized), 403 (default ws), 404 (not found) |
| **Collection**| `GET` | `/api/workspaces/<workspace_id>/collections` (JWT)| `get_collections_by_workspace()` | 200 | 401 (unauthorized) |
| | `POST` | `/api/workspaces/<workspace_id>/collections` (JWT)| `add_collection()` | 201 | 401 (unauthorized), 404 (invalid workspace) |
| | `PATCH`| `/api/collections/<collection_id>` (JWT) | `rename_collection()` | 200 | 400 (missing name), 401 (unauthorized), 404 (not found) |
| | `DELETE`| `/api/collections/<collection_id>` (JWT) | `delete_collection()` | 200 | 401 (unauthorized), 403 (default collection), 404 (not found) |
| **Request** | `POST` | `/api/collections/<collection_id>/requests` (JWT) | `create_request()` | 201 | 401 (unauthorized), 404 (collection not found) |
| | `PATCH`| `/api/requests/<request_id>` (JWT) | `rename_request()`, `update_request_method()`, `save_request()` | 200 | 400 (invalid payload), 401 (unauthorized), 404 (not found) |
| | `DELETE`| `/api/requests/<request_id>` (JWT) | `delete_request()` | 200 | 401 (unauthorized), 404 (not found) |
| **History** | `GET` | `/api/workspaces/<workspace_id>/history` (JWT)| `get_history_entries()` | 200 | 401 (unauthorized), 403 (forbidden), 404 (not found) |
| | `POST` | `/api/workspaces/<workspace_id>/history` (JWT)| `create_history_entry()` | 201 | 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found) |
| **Invitation**| `POST` | `/api/workspaces/<workspace_id>/invitations` (JWT) | `create_invitation()` | 201 | 400 (validation), 401 (unauthorized), 403 (forbidden), 404 (not found) |
| | `GET` | `/api/invitations/pending` (JWT) | `get_pending_invitations()` | 200 | 401 (unauthorized) |
| | `POST` | `/api/invitations/<invitation_id>/accept` (JWT) | `accept_invitation()` | 200 | 400 (not pending), 401 (unauthorized), 403 (forbidden), 404 (not found) |
| | `POST` | `/api/invitations/<invitation_id>/decline` (JWT) | `decline_invitation()` | 200 | 400 (not pending), 401 (unauthorized), 403 (forbidden), 404 (not found) |
| **API Client**| `POST` | `/api/execute` (JWT) | `execute_request()` | 200 | 400 (missing URL/method), 401 (unauthorized), 500 (API error), 504 (timeout) |

---

## 4. Service Layer Design

All business logic, database queries, and transaction commits are isolated in service modules under `backend/services/`.

### 4.1 Service Function Map
* **[jwt_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/jwt_service.py)**:
  * `encode_token(payload, expires_in)`: Encodes a JSON payload into a secure HMAC-SHA256 JWT signature using custom base64url coding.
  * `decode_token(token)`: Decodes and verifies a JWT token signature and expiration.
  * `token_required(f)`: Flask route decorator to enforce token verification via the `Authorization` header.
* **[auth_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/auth_service.py)**:
  * `signup_user(username, first_name, email, password)`: Hashes passwords with `bcrypt` (4 rounds in tests, 12 rounds in production) and calls `create_workspace` to initialize default workspace.
  * `login_user(username, password)`: Queries user record and verifies password match.
* **[workspace_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/workspace_service.py)**:
  * `get_user_workspaces(user_id)`: Fetches workspaces owned by or shared with `user_id`.
  * `create_workspace(user_id, name, is_default)`: Persists new workspace and invokes `ensure_default_collection`.
  * `get_workspace_by_id(workspace_id, user_id)`: Fetches workspace metadata and verifies ownership or membership.
  * `delete_workspace(workspace_id, user_id)`: Deletes workspace if ownership matches and workspace is not default.
* **[invitation_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/invitation_service.py)**:
  * `create_invitation(workspace_id, inviter_id, invitee_username, role)`: Validates and creates a pending invitation with specified role.
  * `get_pending_invitations(user_id)`: Retrieves all pending invitations for a user.
  * `accept_invitation(invitation_id, user_id)`: Marks an invitation accepted and registers workspace membership with the invitation role.
  * `decline_invitation(invitation_id, user_id)`: Marks an invitation declined.
* **[collection_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/collection_service.py)**:
  * `ensure_default_collection(workspace_id)`: Automatically seeds "My Collection" containing two default request items ("Get data", "Post data") if the workspace has no collections.
  * `get_collections_by_workspace(workspace_id)`: Returns all collections (and serialized nested requests) inside the workspace.
  * `add_collection(workspace_id)`: Creates a new collection named "New Collection".
  * `rename_collection(collection_id, new_name)`: Renames custom collection.
  * `delete_collection(collection_id)`: Deletes collection unless it is default.
* **[request_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/request_service.py)**:
  * `create_request(collection_id)`: Seeds a blank GET request.
  * `rename_request(request_id, new_name)`: Updates request display name.
  * `update_request_method(request_id, method)`: Changes request HTTP method (GET, POST, PUT, DELETE).
  * `save_request(request_id, data)`: Saves URL, query params, headers, body, or auth settings to the DB.
  * `delete_request(request_id)`: Deletes saved request configuration.
* **[history_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/history_service.py)**:
  * `get_history_entries(workspace_id, user_id)`: Fetches workspace's request logs for owners/members.
  * `create_history_entry(workspace_id, user_id, history_data)`: Creates and persists a history entry for owners/members.
* **[api_client_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/api_client_service.py)**:
  * `execute_request(method, url, params, headers, body)`: Constructs and executes a proxied HTTP request using the Python `requests` library. Calculates round-trip response time and parses output. *Note: directly returns Flask `jsonify()` responses (known violation).*

---

## 5. Testing Architecture

Backend integration tests reside inside `backend/tests/`. The test environment uses an in-memory SQLite database setup.

### 5.1 Test Fixtures ([conftest.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/conftest.py))
* `app`: Creates a clean in-memory SQLite Flask application context (`sqlite:///:memory:`), creates all tables, and tears them down after each test.
* `client`: Exposes the Flask test client interface for hitting endpoints.
* `registered_user`: Seeds a mock user record.
* `auth_data`: Seeds a mock user, logs them in, and returns workspace metadata.

### 5.2 Test Suites
* **[test_auth.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_auth.py)**: Asserts signup validation, signup duplication errors, and login behavior.
* **[test_workspaces.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_workspaces.py)**: Verifies workspace listings, default workspaces, custom workspace creation, access controls (403 forbidden vs 404 not found), and delete constraints.
* **[test_collections.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_collections.py)**: Asserts auto-seeding of collections, adding collection, renaming collection, and default collection delete limits.
* **[test_requests.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_requests.py)**: Tests request creation, method updates, parameter patching (URL, headers, params, body, auth), deletion, and invalid path validations.
* **[test_execute.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_execute.py)**: Verifies the proxy client behavior (GET, POST JSON parsing, error handling, request timeouts).
* **[test_history.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_history.py)**: Tests request history creation, listings, ownership authorization limits, reverse chronological ordering, and list length caps.
* **[test_invitations.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_invitations.py)**: Tests workspace invitations sending, listing, accepting, declining, and member access verification.

---

## 6. Cross-Cutting Concerns

* **Authentication (Current State)**:
  * Secure JWT-based token authentication is enforced on all protected API routes (workspaces, collections, requests, execute).
  * JWT tokens are passed via the standard `Authorization: Bearer <token>` header.
  * Tokens are generated upon login and verified against a custom SHA256 signature in the backend middleware decorator.
* **SQL Server vs SQLite compatibility**:
  * Development and Production use SQL Server (ODBC Driver 17).
  * Testing uses an in-memory SQLite database. Avoid using database-specific syntax (e.g., MSSQL dialect features) to keep migrations compatible.
* **Legacy SQL Query Syntax**:
  * The codebase heavily relies on legacy Flask-SQLAlchemy `Model.query.filter_by()` or `Model.query.get(id)` syntax.
  * Target style for any new code should use SQLAlchemy 2.0 styled `db.session.get(Model, id)` and `db.session.execute(db.select(Model))` transactions.
