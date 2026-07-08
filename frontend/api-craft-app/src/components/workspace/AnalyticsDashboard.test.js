import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock recharts to avoid SVG rendering issues in JSDOM
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
  LineChart: ({ children }) => <div>{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
  PieChart: ({ children }) => <div>{children}</div>,
  Pie: ({ children }) => <div>{children}</div>,
  Cell: () => <div />,
  Legend: () => <div />,
}));

// Mock useAnalytics hook
jest.mock('../../hooks/useAnalytics', () => () => ({
  data: {
    kpis: { avg_latency: 150.0, p90_latency: 300.0, p95_latency: 450.0, total_requests: 42, error_rate: 10.5 },
    time_series: [{ bucket: '2026-07-08T10:00', avg_latency: 150.0, count: 5 }],
    status_distribution: [
      { category: '2xx', count: 35 },
      { category: '4xx', count: 5 },
      { category: '5xx', count: 2 },
    ],
    slowest_endpoints: [{ url: '/api/users', method: 'GET', avg_latency: 800.0, max_latency: 1200.0 }],
    error_hotspots: [{ url: '/api/items', method: 'DELETE', total_runs: 10, failure_rate: 60.0 }],
  },
  loading: false,
  error: null,
  refresh: jest.fn(),
}));

import AnalyticsDashboard from './AnalyticsDashboard';

describe('AnalyticsDashboard', () => {
  it('renders without crashing and shows KPI values', () => {
    render(<AnalyticsDashboard workspaceId={1} />);
    expect(screen.getByText('Performance Analytics')).toBeTruthy();
    expect(screen.getByText('42')).toBeTruthy();
  });
});
