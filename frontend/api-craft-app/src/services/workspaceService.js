import { authFetch } from './api';

export async function getWorkspaces(userId) {
  const res = await authFetch(`/api/workspaces`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function createWorkspace(userId, name) {
  const res = await authFetch(`/api/workspaces`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getWorkspaceById(workspaceId, userId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}`);
  let data;
  try {
    data = await res.json();
  } catch {
    const err = new Error('Invalid response');
    err.status = res.status;
    throw err;
  }
  if (!res.ok) {
    const err = new Error(data.error);
    err.status = res.status;
    throw err;
  }
  return data;
}

export async function deleteWorkspace(workspaceId, userId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function leaveWorkspace(workspaceId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/leave`, {
    method: 'DELETE',
    skipGlobal403: true,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function renameWorkspace(workspaceId, name) {
  const res = await authFetch(`/api/workspaces/${workspaceId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function updateMemberRole(workspaceId, memberUserId, role) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/members/${memberUserId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function removeMember(workspaceId, memberUserId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/members/${memberUserId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
