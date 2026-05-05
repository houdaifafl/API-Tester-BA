import BASE_URL from './api';

export async function getWorkspaces(userId) {
  const res = await fetch(`${BASE_URL}/api/workspaces?user_id=${userId}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function createWorkspace(userId, name) {
  const res = await fetch(`${BASE_URL}/api/workspaces`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: Number(userId), name }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteWorkspace(workspaceId, userId) {
  const res = await fetch(`${BASE_URL}/api/workspaces/${workspaceId}?user_id=${userId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
