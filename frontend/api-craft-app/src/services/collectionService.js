import { authFetch } from './api';

export async function getCollections(workspaceId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/collections`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function addCollection(workspaceId) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/collections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function renameCollection(collectionId, newName) {
  const res = await authFetch(`/api/collections/${collectionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteCollection(collectionId) {
  const res = await authFetch(`/api/collections/${collectionId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

