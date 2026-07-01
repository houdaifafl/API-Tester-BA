import { authFetch } from './api';

export async function getHistory(workspaceId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/history`);
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Failed to fetch history');
  }
  return data;
}

export async function createHistoryItem(workspaceId, historyItem) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(historyItem),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || 'Failed to create history item');
  }
  return data;
}
