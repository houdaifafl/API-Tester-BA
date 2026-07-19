import { authFetch } from './api';

export async function inviteUserToWorkspace(workspaceId, username, role = 'viewer') {
  const res = await authFetch(`/api/workspaces/${workspaceId}/invitations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, role }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getPendingInvitations() {
  const res = await authFetch('/api/invitations/pending');
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function acceptInvitation(invitationId) {
  const res = await authFetch(`/api/invitations/${invitationId}/accept`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function declineInvitation(invitationId) {
  const res = await authFetch(`/api/invitations/${invitationId}/decline`, {
    method: 'POST',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function cancelInvitation(invitationId) {
  const res = await authFetch(`/api/invitations/${invitationId}`, {
    method: 'DELETE',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}
