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

## Debugging Scenarios to Handle
- Invalid or missing request parameters
- Wrong authentication header injection
- Unresolved `{{variable}}` placeholders
- Broken saved request loading
- Incorrect response parsing (non-JSON responses)
- Inconsistent ORM relationships
