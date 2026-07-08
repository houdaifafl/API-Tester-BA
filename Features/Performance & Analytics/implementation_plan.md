# Implementation Plan — Performance & Analytics Dashboard

This plan describes the full architecture for the **API Performance Monitoring & Response Analytics** dashboard in APICraft. It aggregates existing `history` records on-the-fly using SQLAlchemy and renders them via Recharts in a dedicated dashboard panel.

---

## 1. Feature Summary

The analytics dashboard gives workspace members a visual overview of their API request performance. Users can switch between three timeframes (Last 24 Hours / 7 Days / 30 Days) and see:
- **KPI cards**: Average latency, p90/p95 latency, total throughput, error rate.
- **Line chart**: Average response-time trend over time buckets.
- **Doughnut chart**: HTTP status code distribution (2xx, 3xx, 4xx, 5xx, Network Failures).
- **Slowest Endpoints table**: Top 5 requests by average latency.
- **Error Hotspots table**: Top 5 requests by failure percentage.

All aggregation is performed on-the-fly in SQL using SQLAlchemy aggregation functions. No pre-aggregation table or caching is needed at this scale.

---

## 2. Design Review

### 2.1 Architecture Rationale

**Backend — Pure SQL aggregation in a new service:**
The feature reads from the existing `history` table (`workspace_id`, `method`, `url`, `status`, `response_time`, `created_at`). No new model or table is needed. A single new service file `analytics_service.py` issues four SQL queries per request:
1. KPI aggregate (avg, p90, p95, count, error count).
2. Time-bucket series (grouped by hour or day depending on timeframe).
3. Status-code distribution counts.
4. Per-URL aggregates for slowest + error-hotspot rankings.

A composite index `idx_history_workspace_created` on `(workspace_id, created_at)` is added via `safe_add_column` / raw DDL in `app.py` startup for query speed.

**Why not a separate analytics model?**
No data transformation or pre-aggregation is required at thesis scale. The `history` table already holds all necessary columns. Adding a new table would create duplicate data and maintenance overhead.

**Frontend — New route + isolated hook + two new components:**
- A new `AnalyticsDashboard` component lives under `src/components/workspace/` to stay co-located with other workspace-level views.
- A `useAnalytics(workspaceId, timeframe)` hook owns the loading state, API call, and result caching.
- The dashboard is accessed via a new tab type `'analytics'` handled in `MainPanel.js`.
- A toolbar button in `TopBar.js` (chart line icon) opens the analytics as a special pinned tab.

**Why Recharts?**
As specified in the requirements: React-native, SVG-based, works cleanly with dark themes, supports `ResponsiveContainer`.

### 2.2 State Ownership

| State | Owner | Layer |
|---|---|---|
| `analyticsData` (KPIs, chart series, tables) | `useAnalytics` hook | Feature layer |
| `timeframe` ('24h' / '7d' / '30d') | `AnalyticsDashboard` local `useState` | Local UI layer |
| `loading`, `error` | `useAnalytics` hook | Feature layer |
| Active tab type `'analytics'` | `useWorkspaceTabs` (existing) | Feature layer |

### 2.3 Service Ownership

| Concern | Owner |
|---|---|
| Backend analytics aggregation | `backend/services/analytics_service.py` (new) |
| Backend analytics route | `backend/routes/analytics_routes.py` (new) |
| Frontend API call | `src/services/analyticsService.js` (new) |
| UI state management | `src/hooks/useAnalytics.js` (new) |

`analyticsService.js` follows the exact same `authFetch` + throw-on-error pattern as all other frontend services.

### 2.4 Testing Strategy

**Backend (Tier 1 — pytest):**
- `test_analytics.py` with SQLite in-memory fixture.
- Happy path: authenticated workspace member gets all four data sections with valid history.
- Error path: non-member gets 403; missing workspace gets 404; invalid timeframe gets 400.
- Boundary: empty history returns zeroed KPIs without division-by-zero errors.

**Frontend (Tier 2 — smoke test):**
- `AnalyticsDashboard.test.js`: renders without crash when given mocked `analyticsData` prop.

### 2.5 Scalability Concerns

- **Composite index** on `(workspace_id, created_at)` keeps time-range filtering fast for large history tables.
- **Per-URL aggregation** scans all history rows for the workspace — acceptable for thesis scale. For production a materialized summary table would be preferable.
- **No polling** — analytics data is fetched once on mount and on timeframe change. A manual refresh button is provided.
- **SQLite test compatibility** — p90/p95 are computed Python-side (sort + index) to avoid SQL dialect differences between SQL Server and SQLite.

---

## 3. Files to Create

### 3.1 Backend

| File | ~Lines | Responsibility |
|---|---|---|
| `backend/services/analytics_service.py` | 120 | On-the-fly SQL aggregation: KPIs, time series, status distribution, slowest/error rankings |
| `backend/routes/analytics_routes.py` | 40 | `GET /api/workspaces/<id>/analytics` blueprint |
| `backend/tests/test_analytics.py` | 120 | Pytest integration tests |

### 3.2 Frontend

| File | ~Lines | Responsibility |
|---|---|---|
| `src/services/analyticsService.js` | 20 | `getAnalytics(workspaceId, timeframe)` API call |
| `src/hooks/useAnalytics.js` | 50 | Fetches and exposes analytics data, loading, error, refresh |
| `src/components/workspace/AnalyticsDashboard.js` | ~145 | Dashboard layout: KPI cards, charts, tables, timeframe toggles |
| `src/components/workspace/AnalyticsDashboard.css` | ~120 | Grid layout, KPI card styles, chart containers, dark theme |
| `src/components/workspace/AnalyticsDashboard.test.js` | 20 | Smoke test |

---

## 4. Files to Modify

### 4.1 Backend

| File | Change |
|---|---|
| `backend/app.py` | Import and register `analytics_bp`; add composite index DDL in startup block |

### 4.2 Frontend

| File | Change |
|---|---|
| `src/components/workspace/MainPanel.js` | Add `'analytics'` tab type rendering `<AnalyticsDashboard>` |
| `src/components/workspace/TopBar.js` | Add Analytics icon button (`FaChartLine`) to open analytics tab |
| `src/hooks/useWorkspaceTabs.js` | Expose `openAnalyticsTab()` that opens/focuses a singleton `analytics` tab |
| `backend/openapi.yaml` | Add analytics endpoint spec |

> **Note on component size**: `AnalyticsDashboard.js` is budgeted at ~145 lines which is within the 150-line limit. If it grows beyond this, the KPI cards and charts will be extracted into separate sub-components.

---

## 5. API Contract Changes

### GET `/api/workspaces/<workspace_id>/analytics`
- **Method**: `GET`
- **Security**: JWT Bearer Token
- **Query Params**: `timeframe` — `"24h"` | `"7d"` | `"30d"` (default: `"24h"`)
- **Response 200**:
```json
{
  "kpis": {
    "avg_latency": 243.5,
    "p90_latency": 512.0,
    "p95_latency": 780.0,
    "total_requests": 158,
    "error_rate": 12.7
  },
  "time_series": [
    { "bucket": "2026-07-08T10:00", "avg_latency": 210.0, "count": 14 }
  ],
  "status_distribution": [
    { "category": "2xx", "count": 138 },
    { "category": "3xx", "count": 2 },
    { "category": "4xx", "count": 12 },
    { "category": "5xx", "count": 3 },
    { "category": "Network Failure", "count": 3 }
  ],
  "slowest_endpoints": [
    { "name": "Get Users", "method": "GET", "url": "/api/users", "avg_latency": 812.3, "max_latency": 1540.0 }
  ],
  "error_hotspots": [
    { "name": "Delete Item", "method": "DELETE", "url": "/api/items/1", "total_runs": 20, "failure_rate": 75.0 }
  ]
}
```
- **Response 400**: Invalid `timeframe` value.
- **Response 403**: User not a workspace member.
- **Response 404**: Workspace not found.

---

## 6. OpenAPI Spec Additions

```yaml
  /api/workspaces/{workspace_id}/analytics:
    get:
      summary: Get workspace performance analytics
      security:
        - BearerAuth: []
      parameters:
        - name: workspace_id
          in: path
          required: true
          schema:
            type: integer
        - name: timeframe
          in: query
          required: false
          schema:
            type: string
            enum: ["24h", "7d", "30d"]
            default: "24h"
      responses:
        '200':
          description: Aggregated analytics data
        '400':
          description: Invalid timeframe value
        '403':
          description: Access denied
        '404':
          description: Workspace not found
```

---

## 7. Rule Deviations

- **p90/p95 percentile**: SQL Server and SQLite both lack a portable `PERCENTILE_CONT` function. To maintain SQLite test-environment compatibility, percentile values are computed Python-side by fetching all `response_time` values in the timeframe window and sorting them in memory. For production scale, a native SQL window function would be preferable.
- No other deviations from the AGENTS.md rules.

---

## 8. Verification Plan

### Automated Tests
```bash
# Backend
cd backend
..\venv\Scripts\python -m pytest tests/test_analytics.py -v

# Frontend
cd frontend/api-craft-app
npm test -- --watchAll=false
```

### Manual E2E
1. Send at least 8–10 requests from the app to generate history data.
2. Click the Analytics icon in the TopBar → verify a new **Analytics** tab opens.
3. Verify all four KPI cards render with non-zero values.
4. Verify the **Response Time Trend** line chart renders with data points.
5. Verify the **Status Distribution** doughnut chart shows color-coded slices.
6. Switch timeframe **24h → 7d → 30d** → verify charts update accordingly.
7. Verify the **Slowest Endpoints** and **Error Hotspots** tables render.
8. Test with an **empty workspace** (no history) → zeroed KPIs and "No data" placeholders, no crashes.
