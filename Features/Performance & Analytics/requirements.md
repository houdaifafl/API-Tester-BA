# Requirement Document: API Performance Monitoring & Response Analytics

This document defines the functional requirements and system design choices for aggregating, calculating, and displaying response metrics within a workspace.

---

## 1. Feature Overview
API performance directly impacts user experience. The **API Performance Monitoring & Response Analytics** dashboard provides visual analysis of request latency, error distribution, throughput, and service hotspots.

---

## 2. Core Functional Requirements

### 2.1 Key Performance Indicators (KPIs)
The dashboard must display the following aggregated metrics:
*   **Average Latency**: The average response time (in milliseconds) across all successful/failed requests in the selected timeframe.
*   **Percentile Latency (p90, p95)**: Indicates the latency below which 90% or 95% of request runs fall, helping identify worst-case response times.
*   **Total Throughput**: The total volume of API executions run inside the workspace.
*   **Error Rate**: The percentage of executed requests that returned a status code outside the `2xx` range (including `0`/`null` network connection timeouts).

### 2.2 Visual Charts & Dashboards
The dashboard must render the following interactive visual elements:
1.  **Response Time Trend (Line Chart)**:
    *   Y-axis: Latency (ms)
    *   X-axis: Timeline (Hours or Days depending on timeframe)
    *   Shows average latency trends over time.
2.  **HTTP Status Code Distribution (Doughnut Chart)**:
    *   Breakdown by status categories: `2xx Success` (Green), `3xx Redirection` (Blue), `4xx Client Error` (Orange), `5xx Server Error` (Red), and `Network Timeout/Failed` (Grey).
3.  **Slowest Endpoints Table**:
    *   Ranks the top 5 slowest requests in the workspace, displaying: Request Name, Method, Average Latency, and Max Latency.
4.  **Error Hotspots Table**:
    *   Ranks the top 5 requests with the highest failure rates, displaying: Request Name, Method, Total Runs, and Failure Percentage.

### 2.3 Timeframe Toggles
Users can filter the dashboard data by:
*   `Last 24 Hours` (data grouped by hour)
*   `Last 7 Days` (data grouped by day)
*   `Last 30 Days` (data grouped by day)

---

## 3. Data Flow & Database Architecture
We will leverage the existing [History](file:///c:/Users/hlanj/Bachelor info/Bachelor Arbeit/API tester/backend/models/history_model.py) table for calculations.

*   **Indexes for Performance**:
    *   To keep analytics queries fast, we must ensure a composite database index exists on the `history` table columns: `(workspace_id, created_at)`.
*   **Failed & Timeout Representation**:
    *   Timeout or connection errors (where response time is 0 or status code is missing) must be counted in the metrics as "Network Failures" with a latency value marked as either `0` or maximum timeout configuration to prevent skewing average latency calculations.

---

## 4. Architectural & Technical Choices

### 4.1 On-The-Fly Database Aggregation (Option A)
*   **Behavior**: When a user navigates to the analytics dashboard, the backend triggers on-the-fly SQL queries aggregating [History](file:///c:/Users/hlanj/Bachelor info/Bachelor Arbeit/API tester/backend/models/history_model.py) records in memory using SQLAlchemy functions (e.g. `func.avg()`, `func.count()`).
*   **Performance Optimization**: To maintain fast query response times without pre-aggregation, a composite index `idx_history_workspace_created` on `(workspace_id, created_at)` will be added.

### 4.2 Data Retention Policy
*   **Policy**: No automatic purging or cleanup scheduler will be active. History logs will accumulate indefinitely, ensuring full chronological access to performance trends. Scaling optimizations (such as partitioning or background cleanups) will be deferred until data volumes require it.

### 4.3 Technical UI Choice (Recharts)
*   **Visual Framework**: The frontend will use `Recharts` as the charting library.
*   **Justification**: Recharts is built specifically for React, supports responsive layout wrappers (`ResponsiveContainer`), behaves cleanly with plain CSS styles, and renders sleek SVG charts that fit perfectly within the dark-themed dashboard aesthetics of the application.

