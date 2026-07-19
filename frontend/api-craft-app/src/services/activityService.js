import { authFetch } from './api';

export async function getActivities(workspaceId, limit = 100, offset = 0) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/activities?limit=${limit}&offset=${offset}`);
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || 'Failed to fetch activities');
  }
  return res.json();
}
