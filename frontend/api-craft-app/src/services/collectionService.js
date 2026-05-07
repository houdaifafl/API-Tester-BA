import BASE_URL from './api';

export async function getCollections(workspaceId) {
  const res = await fetch(`${BASE_URL}/api/workspaces/${workspaceId}/collections`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function addCollection(workspaceId) {
  const res = await fetch(`${BASE_URL}/api/workspaces/${workspaceId}/collections`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function renameCollection(collectionId, newName) {
  const res = await fetch(`${BASE_URL}/api/collections/${collectionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteCollection(collectionId) {
  const res = await fetch(`${BASE_URL}/api/collections/${collectionId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function createRequest(collectionId) {
  const res = await fetch(`${BASE_URL}/api/collections/${collectionId}/requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function renameRequest(requestId, newName) {
  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: newName }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function updateRequestMethod(requestId, method) {
  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ method }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteRequest(requestId) {
  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
