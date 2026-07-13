1. Feature Summary
   Implement secure access control for workspace collections list (SEC-09).
   - **Backend**:
     - Create a clean `check_user_read_access(workspace_id, user_id)` function inside `services.workspace_service`.
     - Update the `get_collections_by_workspace(workspace_id, user_id)` service function to enforce read access verification, converting the return type to the standard `(result, error)` tuple pattern.
     - Modify the `list_collections(workspace_id)` route handler in `routes/collection_routes.py` to parse the new return tuple and handle access validation errors by returning appropriate status codes (`403 Forbidden` or `404 Not Found`).

2. Design Review
   2.1 Architecture Rationale
       - Enforcing authorization check in the service layer (`collection_service.py`) using clean utilities from `workspace_service.py` ensures strict business-logic isolation and prevents IDOR vulnerabilities.
       - Converting `get_collections_by_workspace` to the standard `(result, error)` tuple resolves a known architectural inconsistency and aligns fully with Rule 7.3.

   2.2 State Ownership
       - No new state is introduced. Access checks rely on the existing user identity from `g.user_id` inside the authenticated request context.

   2.3 Service Ownership
       - Business authorization check logic resides in `workspace_service.py`.
       - Collection queries reside in `collection_service.py`.

   2.4 Testing Strategy
       - Write integration test cases in `backend/tests/test_collections.py` verifying:
         - **Unauthorized Access**: Attempting to fetch collections of a workspace owned by another user (without membership) returns `403 Forbidden`.
         - **Missing Workspace**: Attempting to fetch collections of a non-existent workspace ID returns `404 Not Found`.
         - **Authorized Access**: Active owner or member (after invitation acceptance) successfully fetches collections with `200 OK`.

   2.5 Scalability Concerns
       - The access check queries `Workspace` and `WorkspaceMember` by ID using indexes, ensuring fast execution.

3. Files to Create
   - None.

4. Files to Modify
   - **[MODIFY] [workspace_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/workspace_service.py)**
     - Implement `check_user_read_access(workspace_id, user_id)`.
   - **[MODIFY] [collection_service.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/services/collection_service.py)**
     - Update `get_collections_by_workspace` to accept `user_id` and check read access, returning a `(result, error)` tuple.
   - **[MODIFY] [collection_routes.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/routes/collection_routes.py)**
     - Update `list_collections` route handler to unpack the new service return tuple and return `403` or `404` error responses.
   - **[MODIFY] [test_collections.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_collections.py)**
     - Append test cases to `TestListCollections` checking IDOR access controls.

5. API Contract Changes
   - `GET /api/workspaces/<workspace_id>/collections` now returns:
     - `403 Forbidden` if the user is not a member/owner of the workspace.
     - `404 Not Found` if the workspace does not exist.

6. OpenAPI Spec Additions
   - Update `GET /api/workspaces/{workspace_id}/collections` path responses in `backend/openapi.yaml` to include `403` and `404` schema references.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_collections.py`
     - Run all backend integration tests to verify no regressions.
