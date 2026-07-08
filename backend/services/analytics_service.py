from datetime import datetime, timedelta
from models.base import db
from models.history_model import History
from models.workspace_model import Workspace
from models.workspace_member_model import WorkspaceMember
from sqlalchemy import func


def _verify_access(workspace_id, user_id):
    """Returns (workspace, error_string). error_string is None on success."""
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, "Workspace not found"
    is_owner = workspace.user_id == user_id
    is_member = WorkspaceMember.query.filter_by(
        workspace_id=workspace_id, user_id=user_id
    ).first() is not None
    if not is_owner and not is_member:
        return None, "Forbidden"
    return workspace, None


def _timeframe_cutoff(timeframe):
    """Returns the earliest datetime that falls within the requested timeframe."""
    now = datetime.utcnow()
    if timeframe == "7d":
        return now - timedelta(days=7)
    if timeframe == "30d":
        return now - timedelta(days=30)
    return now - timedelta(hours=24)   # default: 24h


def _bucket_label(timeframe, dt):
    """Format a datetime into the appropriate bucket label string."""
    if timeframe == "24h":
        return dt.strftime("%Y-%m-%dT%H:00")
    return dt.strftime("%Y-%m-%d")


def _is_error(status):
    """A history entry is a failure if status is None, 0, or outside 2xx/3xx."""
    if status is None or status == 0:
        return True
    return status >= 400


def get_analytics(workspace_id, user_id, timeframe="24h"):
    """
    Aggregate performance metrics for workspace_id over the given timeframe.
    Returns (data_dict, None) on success, (None, error_string) on failure.
    """
    if timeframe not in {"24h", "7d", "30d"}:
        return None, "Invalid timeframe. Must be one of: 24h, 7d, 30d"

    workspace, err = _verify_access(workspace_id, user_id)
    if err:
        return None, err

    cutoff = _timeframe_cutoff(timeframe)

    # Fetch all relevant history entries for the timeframe
    entries = (
        History.query
        .filter(
            History.workspace_id == workspace_id,
            History.created_at >= cutoff
        )
        .order_by(History.created_at.asc())
        .all()
    )

    total = len(entries)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    if total == 0:
        kpis = {
            "avg_latency": 0.0,
            "p90_latency": 0.0,
            "p95_latency": 0.0,
            "total_requests": 0,
            "error_rate": 0.0,
        }
    else:
        latencies = [
            e.response_time if (e.response_time is not None and e.response_time > 0) else 0.0
            for e in entries
        ]
        sorted_lat = sorted(latencies)
        avg_lat = sum(latencies) / total

        def percentile(sorted_vals, pct):
            if not sorted_vals:
                return 0.0
            idx = int(len(sorted_vals) * pct / 100)
            idx = min(idx, len(sorted_vals) - 1)
            return round(sorted_vals[idx], 2)

        errors = sum(1 for e in entries if _is_error(e.status))
        kpis = {
            "avg_latency": round(avg_lat, 2),
            "p90_latency": percentile(sorted_lat, 90),
            "p95_latency": percentile(sorted_lat, 95),
            "total_requests": total,
            "error_rate": round((errors / total) * 100, 2),
        }

    # ── Time Series ──────────────────────────────────────────────────────────
    buckets = {}
    for e in entries:
        label = _bucket_label(timeframe, e.created_at)
        if label not in buckets:
            buckets[label] = {"latencies": [], "count": 0}
        lat = e.response_time if (e.response_time is not None and e.response_time > 0) else 0.0
        buckets[label]["latencies"].append(lat)
        buckets[label]["count"] += 1

    time_series = [
        {
            "bucket": label,
            "avg_latency": round(sum(v["latencies"]) / v["count"], 2),
            "count": v["count"],
        }
        for label, v in sorted(buckets.items())
    ]

    # ── Status Distribution ──────────────────────────────────────────────────
    dist = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "Network Failure": 0}
    for e in entries:
        s = e.status
        if s is None or s == 0:
            dist["Network Failure"] += 1
        elif 200 <= s < 300:
            dist["2xx"] += 1
        elif 300 <= s < 400:
            dist["3xx"] += 1
        elif 400 <= s < 500:
            dist["4xx"] += 1
        else:
            dist["5xx"] += 1

    status_distribution = [
        {"category": cat, "count": cnt} for cat, cnt in dist.items()
    ]

    # ── Per-URL Aggregates (slowest + error hotspots) ─────────────────────────
    url_stats = {}
    for e in entries:
        key = (e.url, e.method)
        if key not in url_stats:
            url_stats[key] = {"latencies": [], "errors": 0, "total": 0}
        lat = e.response_time if (e.response_time is not None and e.response_time > 0) else 0.0
        url_stats[key]["latencies"].append(lat)
        url_stats[key]["total"] += 1
        if _is_error(e.status):
            url_stats[key]["errors"] += 1

    endpoint_rows = []
    for (url, method), stats in url_stats.items():
        n = stats["total"]
        lats = stats["latencies"]
        avg_l = round(sum(lats) / n, 2) if n else 0.0
        max_l = round(max(lats), 2) if lats else 0.0
        failure_rate = round((stats["errors"] / n) * 100, 2) if n else 0.0
        endpoint_rows.append({
            "url": url,
            "method": method,
            "avg_latency": avg_l,
            "max_latency": max_l,
            "total_runs": n,
            "failure_rate": failure_rate,
        })

    slowest = sorted(endpoint_rows, key=lambda r: r["avg_latency"], reverse=True)[:5]
    hotspots = sorted(
        [r for r in endpoint_rows if r["failure_rate"] > 0.0],
        key=lambda r: r["failure_rate"],
        reverse=True
    )[:5]

    return {
        "kpis": kpis,
        "time_series": time_series,
        "status_distribution": status_distribution,
        "slowest_endpoints": slowest,
        "error_hotspots": hotspots,
    }, None
