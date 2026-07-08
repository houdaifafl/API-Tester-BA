import pytest
from datetime import datetime, timedelta
from models.base import db
from models.history_model import History


# ── Helpers ────────────────────────────────────────────────────────────────

def _add_history(client, headers, workspace_id, status, response_time, minutes_ago=5, url="http://api.example.com/data", method="GET"):
    """POST a history entry directly via the API."""
    resp = client.post(
        f"/api/workspaces/{workspace_id}/history",
        json={
            "method": method,
            "url": url,
            "status": status,
            "response_time": response_time,
            "data": {},
        },
        headers=headers,
    )
    assert resp.status_code == 201, f"History creation failed: {resp.get_json()}"
    # Backdate the entry so it falls within the 24h window
    entry = db.session.get(History, resp.get_json()["id"])
    entry.created_at = datetime.utcnow() - timedelta(minutes=minutes_ago)
    db.session.commit()
    return entry


def _get_analytics(client, headers, workspace_id, timeframe="24h"):
    return client.get(
        f"/api/workspaces/{workspace_id}/analytics?timeframe={timeframe}",
        headers=headers,
    )


# ── Happy-path tests ───────────────────────────────────────────────────────

class TestAnalyticsHappyPath:
    def test_returns_200_with_valid_data(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        _add_history(client, headers, ws_id, 200, 150.0)
        _add_history(client, headers, ws_id, 200, 300.0)
        _add_history(client, headers, ws_id, 404, 80.0)

        resp = _get_analytics(client, headers, ws_id)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "kpis" in data
        assert "time_series" in data
        assert "status_distribution" in data
        assert "slowest_endpoints" in data
        assert "error_hotspots" in data

    def test_kpis_values(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        _add_history(client, headers, ws_id, 200, 100.0)
        _add_history(client, headers, ws_id, 200, 200.0)
        _add_history(client, headers, ws_id, 500, 300.0)

        resp = _get_analytics(client, headers, ws_id)
        kpis = resp.get_json()["kpis"]
        assert kpis["total_requests"] == 3
        assert kpis["avg_latency"] == pytest.approx(200.0, rel=0.01)
        assert kpis["error_rate"] == pytest.approx(33.33, rel=0.01)

    def test_status_distribution_categories(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        _add_history(client, headers, ws_id, 200, 100.0)
        _add_history(client, headers, ws_id, 301, 50.0)
        _add_history(client, headers, ws_id, 404, 80.0)
        _add_history(client, headers, ws_id, 500, 200.0)
        _add_history(client, headers, ws_id, None, 0.0)

        resp = _get_analytics(client, headers, ws_id)
        dist = {d["category"]: d["count"] for d in resp.get_json()["status_distribution"]}
        assert dist["2xx"] == 1
        assert dist["3xx"] == 1
        assert dist["4xx"] == 1
        assert dist["5xx"] == 1
        assert dist["Network Failure"] == 1

    def test_slowest_endpoints_max_five(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        for i in range(8):
            _add_history(client, headers, ws_id, 200, float(100 + i * 50),
                         url=f"http://api.example.com/endpoint/{i}")

        resp = _get_analytics(client, headers, ws_id)
        assert len(resp.get_json()["slowest_endpoints"]) <= 5

    def test_timeframe_7d(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        _add_history(client, headers, ws_id, 200, 120.0, minutes_ago=60 * 25)  # 25 h ago — outside 24h but inside 7d
        _add_history(client, headers, ws_id, 200, 80.0, minutes_ago=10)

        resp24 = _get_analytics(client, headers, ws_id, timeframe="24h")
        resp7d = _get_analytics(client, headers, ws_id, timeframe="7d")
        assert resp7d.get_json()["kpis"]["total_requests"] >= resp24.get_json()["kpis"]["total_requests"]

    def test_timeframe_30d(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]
        resp = _get_analytics(client, headers, ws_id, timeframe="30d")
        assert resp.status_code == 200

    def test_error_hotspots_only_contains_failures(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        # Successful endpoint
        _add_history(client, headers, ws_id, 200, 100.0, url="http://api.example.com/success")
        # Failing endpoint
        _add_history(client, headers, ws_id, 500, 150.0, url="http://api.example.com/fail")

        resp = _get_analytics(client, headers, ws_id)
        data = resp.get_json()
        
        # Only the failing one should appear in hotspots
        hotspots = data["error_hotspots"]
        assert len(hotspots) == 1
        assert hotspots[0]["url"] == "http://api.example.com/fail"
        assert hotspots[0]["failure_rate"] == 100.0


# ── Error-path tests ───────────────────────────────────────────────────────

class TestAnalyticsErrorPath:
    def test_invalid_timeframe_returns_400(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]
        resp = _get_analytics(client, headers, ws_id, timeframe="1y")
        assert resp.status_code == 400

    def test_non_member_returns_403(self, client, auth_data):
        # Register a second user
        client.post("/api/auth/signup", json={
            "username": "outsider_analytics",
            "first_name": "Out",
            "email": "outsider_analytics@test.com",
            "password": "Password123!",
        })
        login_resp = client.post("/api/auth/login", json={
            "username": "outsider_analytics",
            "password": "Password123!",
        })
        outsider_token = login_resp.get_json()["token"]
        headers2 = {"Authorization": f"Bearer {outsider_token}"}

        ws_id = auth_data["default_workspace_id"]
        resp = _get_analytics(client, headers2, ws_id)
        assert resp.status_code == 403

    def test_missing_workspace_returns_404(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        resp = _get_analytics(client, headers, 999999)
        assert resp.status_code == 404

    def test_no_auth_token_returns_401(self, client, auth_data):
        resp = client.get(f"/api/workspaces/{auth_data['default_workspace_id']}/analytics")
        assert resp.status_code == 401


# ── Boundary tests ─────────────────────────────────────────────────────────

class TestAnalyticsBoundary:
    def test_empty_history_returns_zeroed_kpis(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        resp = _get_analytics(client, headers, ws_id)
        assert resp.status_code == 200
        kpis = resp.get_json()["kpis"]
        assert kpis["total_requests"] == 0
        assert kpis["avg_latency"] == 0.0
        assert kpis["error_rate"] == 0.0
        assert kpis["p90_latency"] == 0.0
        assert kpis["p95_latency"] == 0.0

    def test_empty_history_no_chart_crash(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        resp = _get_analytics(client, headers, ws_id)
        data = resp.get_json()
        assert isinstance(data["time_series"], list)
        assert isinstance(data["slowest_endpoints"], list)
        assert isinstance(data["error_hotspots"], list)

    def test_null_status_counted_as_network_failure(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        _add_history(client, headers, ws_id, None, 0.0)

        resp = _get_analytics(client, headers, ws_id)
        dist = {d["category"]: d["count"] for d in resp.get_json()["status_distribution"]}
        assert dist["Network Failure"] == 1

    def test_p90_p95_within_range(self, client, auth_data):
        headers = {"Authorization": f"Bearer {auth_data['token']}"}
        ws_id = auth_data["default_workspace_id"]

        for lat in [100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]:
            _add_history(client, headers, ws_id, 200, lat)

        resp = _get_analytics(client, headers, ws_id)
        kpis = resp.get_json()["kpis"]
        assert kpis["p90_latency"] >= kpis["avg_latency"]
        assert kpis["p95_latency"] >= kpis["p90_latency"]
