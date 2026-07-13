import BASE_URL from './api';

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include', // Ensure cookies can be set by the server response
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function signup(username, firstName, email, password) {
  const res = await fetch(`${BASE_URL}/api/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, first_name: firstName, email, password }),
    credentials: 'include',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function logout() {
  const res = await fetch(`${BASE_URL}/api/auth/logout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include', // Ensure cookies are sent so they can be deleted
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

export async function getMe() {
  const res = await fetch(`${BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error);
  return data;
}

