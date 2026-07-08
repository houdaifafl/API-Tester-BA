import React, { useState } from 'react';
import useAnalytics from '../../hooks/useAnalytics';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { FaSyncAlt } from 'react-icons/fa';
import './AnalyticsDashboard.css';

const TIMEFRAMES = [
  { key: '24h', label: 'Last 24 Hours' },
  { key: '7d', label: 'Last 7 Days' },
  { key: '30d', label: 'Last 30 Days' },
];

const STATUS_COLORS = {
  '2xx': '#4caf50',
  '3xx': '#42a5f5',
  '4xx': '#ffa726',
  '5xx': '#ef5350',
  'Network Failure': '#78909c',
};

export default function AnalyticsDashboard({ workspaceId }) {
  const [timeframe, setTimeframe] = useState('24h');
  const { data, loading, error, refresh } = useAnalytics(workspaceId, timeframe);

  if (loading && !data) {
    return <div className="analytics-loading">Loading analytics…</div>;
  }
  if (error) {
    return <div className="analytics-error">Error: {error}</div>;
  }
  if (!data) {
    return <div className="analytics-loading">No analytics data available.</div>;
  }

  const { kpis, time_series, status_distribution, slowest_endpoints, error_hotspots } = data;
  const nonZeroDist = status_distribution.filter(d => d.count > 0);

  return (
    <div className="analytics-dashboard" style={{ userSelect: 'none', cursor: 'default' }}>
      {/* Header */}
      <div className="analytics-header">
        <h2 className="analytics-title">Performance Analytics</h2>
        <div className="analytics-controls">
          <div className="timeframe-group">
            {TIMEFRAMES.map(tf => (
              <button
                key={tf.key}
                className={`tf-btn ${timeframe === tf.key ? 'active' : ''}`}
                onClick={() => setTimeframe(tf.key)}
              >
                {tf.label}
              </button>
            ))}
          </div>
          <button className="refresh-btn" onClick={refresh} title="Refresh data" disabled={loading}>
            <FaSyncAlt className={loading ? 'spinning' : ''} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-label">Avg Latency</span>
          <span className="kpi-value">{kpis.avg_latency.toFixed(1)} <small>ms</small></span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">p90 Latency</span>
          <span className="kpi-value">{kpis.p90_latency.toFixed(1)} <small>ms</small></span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">p95 Latency</span>
          <span className="kpi-value">{kpis.p95_latency.toFixed(1)} <small>ms</small></span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">Total Requests</span>
          <span className="kpi-value">{kpis.total_requests}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">Error Rate</span>
          <span className="kpi-value" style={{ color: kpis.error_rate > 25 ? '#ef5350' : undefined }}>
            {kpis.error_rate.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        {/* Line Chart */}
        <div className="chart-card chart-line">
          <h3 className="chart-title">Response Time Trend</h3>
          {time_series.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={time_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="bucket"
                  tick={{ fill: '#888', fontSize: 11 }}
                  tickFormatter={v => timeframe === '24h' ? v.slice(11, 16) : v.slice(5)}
                />
                <YAxis tick={{ fill: '#888', fontSize: 11 }} unit=" ms" width={60} />
                <Tooltip
                  contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6 }}
                  labelStyle={{ color: '#aaa' }}
                />
                <Line type="monotone" dataKey="avg_latency" stroke="#ffc107" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">No data for this period</div>
          )}
        </div>

        {/* Doughnut Chart */}
        <div className="chart-card chart-doughnut">
          <h3 className="chart-title">Status Distribution</h3>
          {nonZeroDist.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={nonZeroDist}
                  dataKey="count"
                  nameKey="category"
                  cx="50%" cy="50%"
                  innerRadius={50} outerRadius={80}
                  paddingAngle={3}
                  label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                >
                  {nonZeroDist.map((entry, i) => (
                    <Cell key={i} fill={STATUS_COLORS[entry.category] || '#999'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6 }} />
                <Legend wrapperStyle={{ fontSize: 11, color: '#aaa' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="chart-empty">No requests in this period</div>
          )}
        </div>
      </div>

      {/* Tables Row */}
      <div className="tables-row">
        <div className="table-card">
          <h3 className="chart-title">Slowest Endpoints</h3>
          {slowest_endpoints.length > 0 ? (
            <table className="analytics-table">
              <thead><tr><th>Endpoint</th><th>Method</th><th>Avg (ms)</th><th>Max (ms)</th></tr></thead>
              <tbody>
                {slowest_endpoints.map((ep, i) => (
                  <tr key={i}>
                    <td className="ep-url" title={ep.url}>{ep.url}</td>
                    <td><span className="method-chip">{ep.method}</span></td>
                    <td>{ep.avg_latency.toFixed(1)}</td>
                    <td>{ep.max_latency.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="chart-empty">No endpoint data</div>
          )}
        </div>

        <div className="table-card">
          <h3 className="chart-title">Error Hotspots</h3>
          {error_hotspots.length > 0 ? (
            <table className="analytics-table">
              <thead><tr><th>Endpoint</th><th>Method</th><th>Runs</th><th>Fail %</th></tr></thead>
              <tbody>
                {error_hotspots.map((ep, i) => (
                  <tr key={i}>
                    <td className="ep-url" title={ep.url}>{ep.url}</td>
                    <td><span className="method-chip">{ep.method}</span></td>
                    <td>{ep.total_runs}</td>
                    <td style={{ color: ep.failure_rate > 50 ? '#ef5350' : '#ffa726' }}>
                      {ep.failure_rate.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="chart-empty">No error data</div>
          )}
        </div>
      </div>
    </div>
  );
}
