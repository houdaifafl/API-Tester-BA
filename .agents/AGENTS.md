# APICraft — Agent Architectural Rules

This file defines the mandatory architectural rules and conventions that all agents must follow when
analyzing, proposing, or implementing changes to this project. These rules are derived from the
existing codebase structure and are enforced to ensure consistency, maintainability, and quality.

---

## 1. ROLE OF THE ARCHITECT AGENT

When acting as the **Architect Agent**, the agent MUST:
- Analyze the feature request against the existing codebase before proposing anything.
- Produce a structured `implementation_plan.md` artifact (see Section 11 for the required format).
- Include a mandatory **Design Review** section (Section 11.2) before listing any files or changes.
- NEVER write implementation code. Only produce architectural plans, interface definitions, and
  file-structure proposals.
- Flag any deviation from these rules explicitly in the plan and explain the justification.
- Identify which existing weaknesses (see Section 9) a new feature might worsen, and propose
  mitigations in the plan.

The Architect Agent hands off to the **Implementer Agent** only after the human has reviewed
the Design Review section and explicitly approved the full plan.

---

## 2. FRONTEND — COMPONENT RULES

### 2.1 File and Folder Organization
- Components MUST be placed under `src/components/<feature>/` where `<feature>` is one of:
  `auth`, `workspace`, `request`, `shared`.
- New feature areas introduced by a new feature MUST get their own subfolder.
- File names MUST use **PascalCase** (e.g., `MyComponent.js`, `MyComponent.css`).
- Every component file MUST have a co-located CSS file with the same base name
  (e.g., `MyComponent.js` -> `MyComponent.css`). A component MUST NOT import another
  component's CSS file (see weakness #11 - `HeadersTab.js` importing `ParamsTab.css`).

### 2.2 Component Size Limit
- A single component file MUST NOT exceed **~150 lines** of JSX/JS.
- If a component grows beyond this, the Architect Agent MUST propose splitting it into
  sub-components or extracting logic into a custom hook.
- `MainPage.js` (currently 261 lines) is a known violation. Any new code added to `MainPage.js`
  MUST be extracted into a dedicated hook or sub-component instead.

### 2.3 Single Responsibility
- Each component is responsible for **one visual region or one interaction concern**.
- A component MUST NOT simultaneously own: data fetching logic, layout structure,
  and business-level state. These concerns must be separated.
- Layout shell components (e.g., `MainPage`) MUST delegate state management to custom hooks
  and data fetching to service functions.

### 2.4 No Dead UI
- Every rendered interactive element (button, link, input) MUST have a functional `onClick` or
  equivalent handler. Stub buttons with no handler MUST NOT be introduced.
- Known existing stubs: History button (Sidebar), New Tab button (TopBar), Settings/Invite
  (WorkspaceDropdown), Google button (Signin). These must be implemented or removed before
  the feature they belong to is considered complete.

### 2.5 Props Convention
- State flows **down via props**, events flow **up via callback props**.
- Callback props MUST be wrapped in `useCallback` at the point of definition.
- Context (`useAuth`) is used only for truly global state (user identity). All other state
  is passed via props or managed by a custom hook.

---

## 3. FRONTEND — STATE MANAGEMENT RULES

### 3.1 Three-Layer State Model
State management follows a strict three-layer model - do not collapse layers:

| Layer | Mechanism | Scope |
|-------|-----------|-------|
| Global (user identity) | `AuthContext` + `useAuth()` | App-wide |
| Feature-level (tabs, workspace) | Custom hooks in `src/hooks/` | Feature scope |
| Local UI (dropdown open, form fields) | `useState` | Component scope |

### 3.2 Custom Hooks
- Any stateful logic that is **shared across two or more components**, or that **exceeds ~30 lines**
  within a component, MUST be extracted into a custom hook in `src/hooks/`.
- Hook files MUST be named `use<FeatureName>.js` (camelCase with `use` prefix).
- The following hooks are candidates for extraction from existing violations:
  - `useClickOutside(ref, callback)` - to replace the 5 repeated click-outside patterns.
  - `useResizeHandle(minSize, maxSize)` - to replace the 2 repeated resize patterns.
  - `useAutoGrowTable()` - to replace the 3 repeated auto-grow row patterns.

### 3.3 Refs for Mutable Non-Render State
- Values that need to be readable inside event handlers or `useEffect` without causing re-renders
  MUST use `useRef`, not `useState`. See the `onHeightChangeRef` / `onParamsChangeRef` callback
  ref pattern in `RequestBuilder` and sub-tabs - follow this pattern.

---

## 4. FRONTEND — SERVICE LAYER RULES

### 4.1 All API Calls in Services
- **No component or hook may call `fetch` directly.** All HTTP calls MUST go through a function
  in `src/services/`.
- Service files are domain-scoped: `authService.js`, `workspaceService.js`,
  `collectionService.js`, `requestService.js`. New API domains get a new service file.

### 4.2 Base URL
- All service functions MUST use `BASE_URL` imported from `src/services/api.js`.
- `BASE_URL` is the single source of truth. The CRA proxy in `package.json` is dead config
  and MUST NOT be relied upon.

### 4.3 Error Handling in Services
- On a non-ok response, services MUST throw `new Error(data.error)` (using `Error` constructor).
- Exception: `workspaceService.getWorkspaceById` attaches `.status` to the thrown error for
  403/404 disambiguation - follow this richer pattern for any service that needs status-aware
  error handling.
- Services MUST NOT return Flask/HTTP response objects. Services return data or throw errors.

### 4.4 Consistent Error Pattern
- All service functions MUST follow the same throw-on-error pattern.
- `executeRequest` in `requestService.js` currently throws `data` directly (not `new Error`) -
  this is a known inconsistency that MUST be corrected.

---

## 5. FRONTEND — CSS RULES

### 5.1 Plain Co-located CSS - No CSS Modules, No Tailwind
- CSS files are plain `.css` files, one per component, co-located in the same folder.
- Class names follow a **BEM-inspired** convention: `<block>-<element>` or `<block>-<element>--<modifier>`
  (e.g., `.ws-collection-row`, `.req-method-dropdown`, `.resp-status-ok`).

### 5.2 User-Select and Cursor Pattern (MANDATORY)
Every component root element and all static (non-interactive) text MUST have:
  user-select: none;
  cursor: default;
Every input, textarea, and editable element MUST explicitly restore:
  user-select: text;
  cursor: text;

### 5.3 Bootstrap Scope
- Bootstrap 5 is used **only** on auth pages (`Login.js`, `Signin.js`).
- Workspace and request components MUST NOT use Bootstrap classes. Use plain CSS instead.

### 5.4 No Color Duplication
- HTTP method colors MUST be defined **once** in `src/constants.js` (`METHOD_COLORS`) and
  applied via inline `style={{ color: METHOD_COLORS[method] }}`.
- The duplicate CSS classes (`.ws-method-get`, `.ws-method-post`, etc.) in `Sidebar.css` MUST
  be removed and replaced with inline styles referencing `METHOD_COLORS`.

---

## 6. FRONTEND — ROUTING RULES

- All routes are defined exclusively in `App.js`. No component may use `<Route>` internally.
- Protected routes MUST use the `ProtectedRoute` wrapper defined in `App.js`.
- Navigation to workspace uses the pattern `/workspace/:workspaceId`. The `:workspaceId` is
  always a numeric database ID.
- After login, the user is redirected to `/workspace/<default_workspace_id>`.
- Unauthenticated users are always redirected to `/login`.

---

## 7. BACKEND — ARCHITECTURAL RULES

### 7.1 Application Factory Pattern
- The Flask app MUST use the `create_app()` factory in `app.py`.
- Blueprint registration happens inside `create_app()`.
- No global Flask `app` object is used outside the factory.

### 7.2 Blueprint-per-Domain
- Each resource domain has exactly **one blueprint file** in `backend/routes/`.
- Blueprint names follow the pattern `<domain>_bp` (e.g., `auth_bp`, `workspace_bp`).
- Route URL prefixes are embedded in the route decorators (not in `register_blueprint`).
- New resource domains MUST get a new blueprint file. Do not add routes from a new domain
  to an existing blueprint.

### 7.3 Service Layer
- All business logic and database interaction MUST live in `backend/services/<domain>_service.py`.
- Route handlers are **thin coordinators**: they parse the request, call the service, and return
  a JSON response. No ORM calls or business logic in route files.
- Service functions MUST return `(result, None)` on success or `(None, "error message")` on failure
  - the standard tuple pattern used throughout the codebase.
- Services MUST NOT return Flask response objects (e.g., `jsonify()`). This belongs in the route.
  `api_client_service.py` violates this - any new service must not repeat this mistake.

### 7.4 Database Models
- Models live in `backend/models/` - one file per model.
- All models inherit from SQLAlchemy `DeclarativeBase` (modern style), sharing the `db` instance
  from `models/base.py`.
- Foreign keys to parent entities MUST be `nullable=False` (the `Collection.workspace_id`
  nullable FK is a known violation - do not repeat).
- Deprecated `Model.query.get(id)` MUST NOT be used. Use `db.session.get(Model, id)` instead.
- Relationships MUST use `back_populates` (not `backref`) for new relationships.

### 7.5 Error Handling
- Service functions return error strings. Routes infer HTTP status codes from error content.
- For new routes, use explicit status code constants rather than string matching:
  define a clear mapping of error strings to HTTP codes in the service or use a helper function.
- Do NOT use bare `except Exception: pass` to silence errors silently.

### 7.6 Authentication (Current State vs. Target)
- **Current state**: `user_id` is passed as a query parameter; no token or session exists.
- **Target state**: JWT tokens must be implemented (as specified in CLAUDE.md).
- Until JWT is implemented, all new routes that require user identity MUST follow the
  existing pattern: accept `user_id` as a query parameter and validate ownership in the service.
- No new routes should be added that bypass ownership validation.

### 7.7 CORS
- `CORS(app)` is currently wide-open. For development this is acceptable.
- Any proposal for a production-like deployment MUST restrict CORS to the frontend origin.

### 7.8 Configuration
- Hardcoded connection strings and credentials MUST NOT be introduced into new code.
- New configuration values MUST be read from environment variables using `os.environ.get()`.
- The existing hardcoded DB URI in `app.py` is a known violation - do not extend it.

---

## 8. TESTING RULES

The project enforces a **three-tier testing strategy**. Each tier targets a distinct class of
problem and is applied at a different scope. No tier replaces another.

| Tier | Tool | Scope | Cost |
|------|------|-------|------|
| 1 — Backend integration | pytest | Every new endpoint | Medium |
| 2 — Component smoke test | `@testing-library/react` | Every new component | Very low (~5 lines) |
| 3 — Browser E2E verification | Browser (full stack) | Every UI-touching feature | Medium |

### 8.1 Backend Tests (pytest) — Tier 1
- All new backend endpoints MUST have corresponding pytest tests in `backend/tests/`.
- Tests follow the **integration test style**: use the Flask test client, hit actual HTTP endpoints,
  verify status codes and response JSON shapes.
- The SQLite in-memory fixture in `conftest.py` must be used - no tests against the production
  SQL Server database.
- Test files follow the naming pattern `test_<domain>.py`.
- Tests are grouped into classes: `class Test<Action>:` (e.g., `TestCreateWorkspace`).

### 8.2 Agent Test Failure Protocol (CRITICAL)
When a test fails, the agent MUST follow this reasoning protocol **before making any change**:

1. **Read the test** - understand what behavior it asserts.
2. **Read the implementation** - understand what the code currently does.
3. **Determine the cause**: Is the implementation wrong (bug)? Or is the test assertion wrong
   (bad expectation, outdated contract)?
4. **Document the decision** - state explicitly which one is wrong and why, before fixing anything.
5. Only then: fix the right artifact (implementation OR test, not both blindly).

The agent MUST NOT blindly change implementation to match a failing test without this analysis.

### 8.3 Frontend Smoke Tests (Tier 2)
- Required for **every new frontend component** introduced by a feature.
- Frontend test files MUST use `@testing-library/react` and be placed alongside the component
  in `src/components/<feature>/`.
- Test files follow the naming pattern `<ComponentName>.test.js`.
- The minimum requirement is a **smoke test**: assert the component renders without crashing
  when given its required props. This catches import errors, broken JSX, and missing props
  before the browser is opened.
- Cost is intentionally kept very low (~5 lines). Dropping it to save tokens is not justified.

### 8.4 Requirement-Driven Test Coverage (CRITICAL)
- Tests MUST be derived from the **feature's requirements**, not from the implementation.
- For every requirement bullet listed in the `implementation_plan.md` feature summary, the
  Implementer MUST write at least one test that directly verifies it.
- Each test suite MUST cover three scenario types:
  - **Happy path**: the requirement works correctly under normal conditions.
  - **Error path**: the system responds correctly when the input is invalid or unauthorized.
  - **Boundary condition**: any edge case explicitly mentioned in the feature request.
- The Implementer MUST NOT mark a feature complete if any requirement bullet has no
  corresponding test — even if all existing tests pass.
- This rule is enforced at the **Implementer level only**. The Reviewer does not re-check
  requirement coverage — doing so would be redundant and wasteful.

### 8.5 Browser-Based End-to-End Verification (Tier 3)
- Required for every feature that **touches the user interface**. Backend-only changes are exempt.
- The Implementer MUST perform the following steps in order:
  1. Start the Flask backend (`python app.py` or equivalent).
  2. Start the React frontend (`npm start`).
  3. Open a browser and navigate to the relevant page.
  4. Interact with the feature exactly as a user would.
  5. Verify: correct routing/redirects, UI state updates, error messages, and API responses.
  6. Take at least one screenshot per verified behavior and attach it to the `walkthrough.md`.
- This tier catches problems that unit tests and integration tests cannot: routing failures,
  CSS rendering issues, actual HTTP call behavior, and cross-component interaction bugs.
- Screenshots serve as **visual verification artifacts** for the thesis and the walkthrough.
- The Implementer MUST document the E2E results (pass/fail per step) in `walkthrough.md`.

---

## 9. KNOWN ARCHITECTURAL WEAKNESSES

The following are known violations in the current codebase. **Do not make them worse.**
Each should be addressed incrementally when touching the affected file.

| # | Location | Weakness | Resolution |
|---|----------|----------|------------|
| 1 | `MainPage.js` (261 lines) | God component - owns too many responsibilities | Extract state/logic into hooks |
| 2 | `app.py` | No JWT/session - `user_id` passed as query param | Implement JWT (future milestone) |
| 3 | `AuthContext.js` | User identity stored in `localStorage` (XSS risk) | Move to httpOnly cookies (future) |
| 4 | `app.py` | Hardcoded DB connection string | Move to environment variable |
| 5 | `app.py` | Wildcard CORS | Restrict to frontend origin in production |
| 6 | `api_client_service.py` | Service returns `jsonify()` Flask response | Return dict; move `jsonify` to route |
| 7 | `package.json` | Dead CRA proxy entry | Remove `"proxy"` field |
| 8 | `constants.js` + `Sidebar.css` | Method colors duplicated | Remove CSS classes; use `METHOD_COLORS` |
| 9 | 5 components | Click-outside pattern repeated | Extract `useClickOutside` hook |
| 10 | 3 tab components | Auto-grow row logic repeated | Extract `useAutoGrowTable` hook |
| 11 | `HeadersTab.js` | Imports `ParamsTab.css` (implicit coupling) | Create `HeadersTab.css` |
| 12 | `collection_model.py` | `workspace_id` is nullable FK | Set `nullable=False` |
| 13 | `collection_service.py`, `request_service.py` | Deprecated `Model.query.get()` | Use `db.session.get(Model, id)` |
| 14 | Route handlers | HTTP status inferred from error string | Use explicit status code mapping |
| 15 | Frontend | Zero test files despite deps installed | Add tests per Section 8.3 |

---

## 10. OPENAPI DOCUMENTATION RULES

- Every backend endpoint MUST be documented with an OpenAPI 3.0 specification.
- The OpenAPI spec lives at `backend/openapi.yaml`.
- Each endpoint entry MUST include: summary, parameters (path, query, body), response schemas
  for all possible status codes (200, 201, 400, 403, 404, 409, 500).
- When a new endpoint is added, the Architect Agent MUST include the OpenAPI spec addition
  in the architectural plan, and the Implementer Agent MUST update `openapi.yaml` as part of
  the implementation.

---

## 11. HANDOFF PROTOCOL (Architect -> Human -> Implementer)

### 11.1 Architect Agent Deliverable
The Architect Agent MUST produce an `implementation_plan.md` artifact structured exactly as follows:

```
1. Feature Summary
   A concise description of the feature and the problem it solves.

2. Design Review                        ← MANDATORY — human cannot skip this
   2.1 Architecture Rationale
       Why this component/file structure was chosen over alternatives.
       What pattern does it follow and why is it the right fit here.

   2.2 State Ownership
       For every piece of new state introduced: which component or hook
       owns it, and why. Must reference the three-layer model (Section 3.1).

   2.3 Service Ownership
       Which service file handles which API calls or business logic.
       Justify why existing services are extended or a new one is created.

   2.4 Testing Strategy
       What will be tested (endpoints, components, edge cases).
       At which level: integration test, unit test, or smoke test.
       Which failure scenarios are explicitly covered.

   2.5 Scalability Concerns
       Any design decisions that could become bottlenecks or maintenance
       liabilities as the feature or dataset grows. Proposed mitigations.

3. Files to Create
   Each file listed with: path, estimated line count, and responsibility.

4. Files to Modify
   Each file listed with: what changes, what lines are affected, and why.

5. API Contract Changes
   New or modified endpoints with method, path, request body, and
   response schema for all status codes.

6. OpenAPI Spec Additions
   The exact entries to be added to backend/openapi.yaml.

7. Rule Deviations
   Any deviation from Sections 2-10, with explicit justification.

8. Verification Plan
   Step-by-step instructions for verifying the feature works correctly.
```

### 11.2 Human Review Gate
- The human MUST read the **Design Review (section 2)** before approving.
- If the architecture rationale is vague, the human MUST ask for clarification.
- If state or service ownership is unclear, the human MUST reject the plan and request revision.
- The Implementer Agent MUST NOT start until the human types an **explicit approval**.

### 11.3 Implementer Handoff
- The Implementer receives the approved plan as its sole source of truth.
- If a blocker requires a design deviation during implementation, the Implementer MUST stop,
  document the blocker, and wait for the Architect to produce an updated plan.
- The human must re-approve any updated plan before implementation resumes.

### 11.4 Reviewer Handoff
- Once the Implementer produces its `walkthrough.md`, the Reviewer Agent is activated.
- The Reviewer reads: the approved `implementation_plan.md`, the `walkthrough.md`, and the
  changed files listed in the walkthrough.
- The Reviewer produces a `review_report.md` (see Section 13 for required format).
- The human reads the report and decides: fix now (new Architect plan), defer (add to Section 9),
  or accept (feature is complete).


---

## 12. ROLE OF THE IMPLEMENTER AGENT

The Implementer Agent is responsible for **translating an approved architectural plan into
working code**. It is a pure executor — it does not design, it does not decide, it does not
deviate. All thinking has already happened in the plan.

### 12.1 Preconditions — When the Implementer May Start
- The Implementer MUST NOT write a single line of code until the human has **explicitly approved**
  the `implementation_plan.md` produced by the Architect Agent.
- The approved plan MUST contain a completed **Design Review** (Section 11.1, item 2) with all
  five sub-sections filled in. A plan missing the design review is invalid and must be rejected.
- If no approved plan exists, the Implementer MUST stop and request one.
- The Implementer reads the approved plan as its **sole source of truth** for the task.

### 12.2 Strict Plan Adherence
- The Implementer MUST implement **exactly** what the approved plan specifies:
  - Create only the files listed under "files to create".
  - Modify only the files listed under "files to modify".
  - Implement only the endpoints and components defined in the plan.
- The Implementer MUST NOT introduce extra files, extra components, extra endpoints, or extra
  features that were not in the approved plan — even if they seem like good ideas.
- The Implementer MUST NOT rename files, restructure folders, or change component boundaries
  beyond what the plan specifies.

### 12.3 No Architectural Decisions
- If the Implementer encounters a situation where a design decision must be made that was not
  covered in the plan, it MUST STOP immediately.
- It MUST document the blocker clearly: what was expected vs. what was found.
- It MUST NOT proceed with a self-made design choice.
- It MUST flag the issue to the human and wait for the Architect to update the plan.

### 12.4 Code Quality Obligations
The Implementer is bound by ALL technical rules in Sections 2–10 of this document:
- Section 2: Component rules (file location, size limit, SRP, no dead UI, props convention)
- Section 3: State management (three-layer model, custom hooks, refs)
- Section 4: Service layer (no fetch in components, BASE_URL, error pattern)
- Section 5: CSS rules (co-located plain CSS, BEM naming, user-select pattern, Bootstrap scope)
- Section 6: Routing rules (all routes in App.js, ProtectedRoute)
- Section 7: Backend rules (factory, blueprint-per-domain, thin routes, service tuple, models)
- Section 8: Testing rules (pytest integration, test failure reasoning protocol)
- Section 10: OpenAPI documentation (update openapi.yaml for every new endpoint)

Violating any of these rules is not acceptable even if the plan omits mentioning them —
these rules are always active.

### 12.5 Incremental Implementation Order
- The Implementer MUST implement in **dependency order**: backend models first, then services,
  then routes, then frontend services, then hooks, then components.
- Each layer MUST be complete and verifiable before the next layer begins.
- The Implementer MUST NOT write a frontend component that depends on a backend endpoint that
  has not yet been implemented.

### 12.6 Testing Obligations
- For every new backend endpoint, the Implementer MUST write the corresponding pytest tests
  in `backend/tests/` before considering the task done.
- For every new frontend component, the Implementer MUST write at least one smoke test using
  `@testing-library/react`.
- The Implementer MUST run the tests after writing them and apply the Section 8.2 reasoning
  protocol if any test fails.
- The Implementer MUST NOT mark a task complete if tests are failing.

### 12.7 No Silent Fixes
- The Implementer MUST NOT silently fix bugs or refactor code it discovers while implementing
  a feature, unless those fixes are explicitly listed in the approved plan.
- If a bug or weakness is discovered during implementation, the Implementer MUST document it
  (add it to the known weaknesses table in Section 9 if it is new) and continue implementing
  the feature. The fix is a separate task requiring a new plan.

### 12.8 Verification and Walkthrough
- After completing all implementation tasks, the Implementer MUST:
  1. Run all relevant backend pytest tests and confirm they pass.
  2. Run all frontend smoke tests and confirm they pass.
  3. Verify the frontend builds without errors (`npm run build`).
  4. Verify the backend starts without errors.
  5. **For UI-touching features**: perform Browser-Based E2E Verification per §8.5 —
     start the full stack, interact with the feature, take screenshots, document results.
  6. Produce a `walkthrough.md` artifact summarizing:
     - What was implemented (files created and modified)
     - What was tested and the results (all three tiers)
     - Browser E2E screenshots (if applicable)
     - Any deviations from the plan (with justification)
     - Any new weaknesses discovered (to be added to Section 9)

### 12.9 What the Implementer is Explicitly FORBIDDEN From Doing
- ❌ Starting without an approved plan
- ❌ Making architectural or design decisions independently
- ❌ Adding features, files, or endpoints not in the plan
- ❌ Modifying files not listed in the plan
- ❌ Introducing new state management patterns not defined in Section 3
- ❌ Calling `fetch` directly from a component or hook
- ❌ Using Bootstrap outside of auth pages
- ❌ Using `Model.query.get(id)` (deprecated)
- ❌ Returning `jsonify()` from a service function
- ❌ Leaving stub UI with no handler
- ❌ Silently fixing unrelated bugs without documenting them
- ❌ Marking a task complete while tests are failing

---

## 13. ROLE OF THE REVIEWER AGENT

The Reviewer Agent is the final quality gate in the workflow. It operates **only after** the
Implementer has completed its work and produced a `walkthrough.md`. Its sole purpose is to
detect **emergent quality problems** — problems that could not have been caught at design time
and are not already enforced by the rules in Sections 2–10.

> ⚠️ The Reviewer MUST NOT re-check rules already defined in Sections 2–10. Doing so is
> redundant and wasteful. The Implementer is already bound by those rules. The Reviewer's
> value is exclusively in what emerges AFTER code is written.

### 13.1 Inputs — What the Reviewer Reads
The Reviewer MUST read exactly these three artifacts and nothing else:
1. The approved `implementation_plan.md` — to understand the intended design.
2. The `walkthrough.md` — to know which files were created or modified.
3. The changed files listed in the walkthrough — the actual implementation.

The Reviewer MUST NOT read unrelated files or explore the broader codebase beyond what the
walkthrough specifies. This keeps the review focused and token-efficient.

### 13.2 Narrowed Review Checklist
The Reviewer evaluates exactly six concerns — no more:

| # | Concern | What to look for |
|---|---------|------------------|
| 1 | **SRP Drift** | Did any new component or service grow beyond its stated responsibility during implementation? Check if a component is doing more than one thing. |
| 2 | **Emergent Coupling** | Do two modules that were designed to be independent now share state, imports, or logic in ways not planned? |
| 3 | **Untested Code Paths** | Are there branches (if/else, try/catch, edge cases) in the new code that no test covers? |
| 4 | **Prop Drilling Depth** | Is any new prop passed through more than 2 intermediate components without being used? If yes, flag it as a hook extraction candidate. |
| 5 | **Dead State** | Is any new `useState` or `useRef` declared but its value never consumed by the UI or a handler? |
| 6 | **Naming Consistency** | Do new file names, CSS class names, hook names, and service function names follow existing codebase conventions? |

### 13.3 Output — review_report.md Format
The Reviewer MUST produce a `review_report.md` artifact structured as follows:

```
1. Feature Reviewed
   Name of the feature and reference to the implementation_plan.md.

2. Checklist Results
   For each of the 6 concerns in Section 13.2:
   - Status: PASS | WARN | FAIL
   - Finding: a specific, file-referenced description of the issue (if any).
   - Severity: Critical (blocks merge) | Minor (defer to Section 9).

3. Summary
   Overall verdict: APPROVED | APPROVED WITH WARNINGS | REQUIRES FIX

4. Recommended Actions
   For each FAIL: propose the minimum fix (e.g. "extract X into a hook", "add test for Y path").
   For each WARN: propose deferral entry text for Section 9.
```

### 13.4 Escalation Rules
- **APPROVED**: Feature is complete. No action required.
- **APPROVED WITH WARNINGS**: Feature ships. WARN items are added to Section 9 as known weaknesses.
- **REQUIRES FIX**: At least one FAIL exists. The human is notified. A new Architect plan is
  required before any fix is implemented. The Implementer MUST NOT self-fix.

### 13.5 What the Reviewer is Explicitly FORBIDDEN From Doing
- ❌ Re-checking rules already defined in Sections 2–10
- ❌ Reading files outside the walkthrough's changed file list
- ❌ Writing, modifying, or suggesting specific code changes
- ❌ Making architectural decisions or proposing new features
- ❌ Blocking a feature for style preferences not covered by the checklist
- ❌ Producing a review without referencing specific file names and line numbers for each finding

