import BASE_URL from './api';

export async function executeRequest(payload) {
  const res = await fetch(`${BASE_URL}/api/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw data;
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

export async function saveRequest(requestId, data) {
  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  const responseData = await res.json();
  if (!res.ok) throw new Error(responseData.error);
  return responseData;
}

export async function deleteRequest(requestId) {
  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
