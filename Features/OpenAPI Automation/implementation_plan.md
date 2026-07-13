1. Feature Summary
   Implement an automated OpenAPI documentation drift validation test suite. This test checks that all Flask routes, HTTP methods, and path parameters match `openapi.yaml` to prevent documentation drift.
   - **OpenAPI Configuration**:
     - Fix structural formatting bug in `openapi.yaml` by moving the `components:` block from the middle of the file (lines 588-691) to the end of the file. This allows all paths to be parsed contiguously under the root `paths:` block.
   - **Dependencies**:
     - Add `pyyaml` to `backend/requirements` to parse the YAML file in test suites.
   - **Test Suite**:
     - Create a test file `backend/tests/test_openapi_drift.py` that verifies:
       - Every Flask route (excluding `/` and static endpoints) is documented in `openapi.yaml`.
       - Every documented OpenAPI path exists as an active Flask route.
       - Every documented HTTP method is allowed on the corresponding Flask route.
       - Every active HTTP method on a route is documented in the OpenAPI path.

2. Design Review
   2.1 Architecture Rationale
       - Using decorators to generate OpenAPI documentation dynamically adds severe code clutter, vendor lock-in (e.g. to a specific Flask extension), and runtime overhead.
       - A standalone validation test suite verifies compatibility between code routing and documentation at test time. This keeps python route files clean, preserves standard YAML documentation, and guarantees zero drift.

   2.2 State Ownership
       - No state is introduced.

   2.3 Service Ownership
       - Run as a test suite during pytest integration checking.

   2.4 Testing Strategy
       - The validation test itself acts as the test suite checking route coverage and specification alignment.
       - Exclude the home testing route `/` from the check as it is a diagnostic endpoint.

   2.5 Scalability Concerns
       - None.

3. Files to Create
   - **[NEW] [test_openapi_drift.py](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/tests/test_openapi_drift.py)** (Est: ~60 lines)
     - Test comparing Flask's `url_map` against `openapi.yaml`.

4. Files to Modify
   - **[MODIFY] [requirements](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/requirements)**
     - Register `pyyaml`.
   - **[MODIFY] [openapi.yaml](file:///c:/Users/hlanj/Bachelor%20info/Bachelor%20Arbeit/API%20tester/backend/openapi.yaml)**
     - Move lines 588 to 691 (the `components:` block) to the end of the file.

5. API Contract Changes
   - None.

6. OpenAPI Spec Additions
   - Corrects structural parsing of existing paths.

7. Rule Deviations
   - None.

8. Verification Plan
   - **Automated Tests**:
     - Run `pytest backend/tests/test_openapi_drift.py`.
     - Run the entire test suite `pytest` to confirm 100% pass status.
