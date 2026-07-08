import { authFetch } from './api';

/**
 * Fetch analytics aggregates for a workspace.
 * @param {number} workspaceId
 * @param {'24h'|'7d'|'30d'} timeframe
 */
export async function getAnalytics(workspaceId, timeframe = '24h') {
  const res = await authFetch(
    `/api/workspaces/${workspaceId}/analytics?timeframe=${timeframe}`
  );
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to load analytics');
  return data;
}
