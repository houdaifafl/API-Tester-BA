import { authFetch } from './api';

export async function getComments(workspaceId, requestId = null) {
  let url = `/api/workspaces/${workspaceId}/comments`;
  if (requestId) {
    url += `?request_id=${requestId}`;
  }
  const res = await authFetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function postComment(workspaceId, payload) {
  const res = await authFetch(`/api/workspaces/${workspaceId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function editComment(commentId, content) {
  const res = await authFetch(`/api/comments/${commentId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function deleteComment(commentId) {
  const res = await authFetch(`/api/comments/${commentId}`, {
    method: 'DELETE'
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
