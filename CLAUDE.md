# APICraft — Project Context

## Overview
APICraft is a fullstack web application for API collaboration and testing. Users can organize API requests into collections, execute and inspect HTTP calls, manage variables and authentication settings, document endpoints, and persist reusable request configurations.

## Tech Stack
- **Backend:** Python, Flask, SQLAlchemy, SQL Server Express (ODBC Driver 17)
- **Frontend:** React (functional components, hooks, Context API)
- **Auth:** JWT + Flask-Login

## Project Structure
```
API tester/
├── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   └── services/
└── frontend/          ← to be created
```

## Core Modules
1. **Workspace & Overview** — top-level container; users can own and switch between multiple workspaces
2. **Collections & Request Organization** — create, rename, delete collections; sidebar navigation
3. **Request Builder & Execution** — GET, POST, PUT, DELETE with params, headers, body
4. **Response Analysis** — display status code, response time, formatted JSON body
5. **Saved Requests & Persistence** — save, retrieve, update request definitions linked to collections
6. **Authentication Management** — No Auth, Bearer Token, API Key, Basic Auth (per request or per collection)

## Backend Guidelines (Flask)
- Use **Flask Blueprints** for route organization
- All endpoints must handle GET, POST, PUT, DELETE where applicable
- Use **JWT** for token-based auth and **Flask-Login** for session management
- Validate all inputs; return meaningful error responses
- Implement structured logging for all significant actions

## Frontend Guidelines (React)
- Use **functional components** and React hooks only (no class components)
- Use **Context API** for global state management
- Use **CSS Modules** or styled-components for styling
- Ensure responsive design and accessibility best practices
- All API calls go through a centralized service layer (no raw fetch/axios in components)

## React Architecture Rules (enforce on every new component)
- **File naming:** All component files must be PascalCase (e.g. `Sidebar.js`, not `sidebar.js`)
- **Folder structure:** Group components by feature under `src/components/<feature>/`. Shared/reusable pieces go in `src/components/shared/`. Auth pages go in `src/components/auth/`
- **Service layer:** Every API call must live in `src/services/`. Components import and call service functions — they never construct `fetch` calls themselves. The base URL lives only in `src/services/api.js`
- **Component size:** If a component exceeds ~100 lines or handles more than one visual region, split it. Pages are layout shells that own state; sub-components are presentational and receive props
- **State ownership:** State lives at the lowest parent that needs to share it. Do not duplicate state across siblings. Do not read `localStorage` in more than one place — lift it into a context or the top-level parent
- **No dead files:** Delete placeholder, boilerplate, or abandoned components immediately — do not leave them in the tree

## Agent Role & Behavior
- You are the **primary developer** for both the backend (Flask) and frontend (React) of this application
- Follow best practices at all times — security, readability, and maintainability take priority
- **Explain your logic** when implementing non-trivial decisions (architecture choices, trade-offs, patterns used)
- Generated code must be **modular, maintainable, and scalable** — avoid tightly coupled or monolithic implementations
- Proactively **suggest improvements** if you identify a better approach, but do not implement them without confirmation
- Always consider the **full system** (both frontend and backend) when making decisions — changes in one layer may affect the other

## Coding Conventions
- Keep logic out of route handlers — delegate to service functions
- One responsibility per file; avoid large monolithic modules
- Do not add speculative features or abstractions beyond what is asked
- Do not add comments unless the logic is non-obvious
- Always think about performance implications of every implementation decision — misleading patterns in both frontend and backend can introduce subtle performance issues

## CSS Conventions
- **Cursor & text selection:** Every page/view must disable text selection and set a default cursor on its root container and all static text (labels, titles, footer text, dividers). Input and textarea elements must explicitly restore `user-select: text` and `cursor: text`. Use this pattern for every new CSS file:
  ```css
  /* root container */
  .page-root, .card {
    user-select: none;
    cursor: default;
  }
  /* static text */
  .title, .label, .footer-text {
    user-select: none;
  }
  /* inputs */
  .input-field, textarea {
    user-select: text;
    cursor: text;
  }
  ```

## Pre-Deployment Checklist
- **Switch off the Werkzeug dev server:** `app.run(debug=True)` in [app.py](backend/app.py) is for development only. Before any real deployment, replace it with a production WSGI server: `gunicorn -w 4 "app:create_app()"`. Debug mode adds per-request overhead and the dev server is not designed for concurrent load.

## Debugging Scenarios to Handle
- Invalid or missing request parameters
- Wrong authentication header injection
- Unresolved `{{variable}}` placeholders
- Broken saved request loading
- Incorrect response parsing (non-JSON responses)
- Inconsistent ORM relationships
