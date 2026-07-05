import { authFetch } from './api';

export async function getAdminUsers() {
  const res = await authFetch('/api/admin/users');
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function suspendUser(userId) {
  const res = await authFetch(`/api/admin/users/${userId}/suspend`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function reactivateUser(userId) {
  const res = await authFetch(`/api/admin/users/${userId}/reactivate`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteUser(userId) {
  const res = await authFetch(`/api/admin/users/${userId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function promoteUser(userId) {
  const res = await authFetch(`/api/admin/users/${userId}/promote`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function demoteUser(userId) {
  const res = await authFetch(`/api/admin/users/${userId}/demote`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getAdminWorkspaces() {
  const res = await authFetch('/api/admin/workspaces');
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteWorkspaceByAdmin(workspaceId) {
  const res = await authFetch(`/api/admin/workspaces/${workspaceId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getWorkspaceCollectionsByAdmin(workspaceId) {
  const res = await authFetch(`/api/admin/workspaces/${workspaceId}/collections`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteCollectionByAdmin(collectionId) {
  const res = await authFetch(`/api/admin/collections/${collectionId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function logSensitiveView(workspaceId, details) {
  const res = await authFetch(`/api/admin/workspaces/${workspaceId}/log-view`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ details }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getAuditLogs(limit = 100, offset = 0) {
  const res = await authFetch(`/api/admin/audit-logs?limit=${limit}&offset=${offset}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getUserNotifications() {
  const res = await authFetch('/api/notifications');
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function markNotificationsRead() {
  const res = await authFetch('/api/notifications/read', {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
