import { API_BASE } from './config.js';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  const data = await res.json();
  if (!res.ok) {
    const message =
      data.detail ||
      Object.values(data).flat().join(' ') ||
      'An error occurred.';
    const err = new Error(message);
    err.data = data;
    throw err;
  }
  return data;
}

export function isLoggedIn() {
  return !!localStorage.getItem('access_token');
}

export function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_role');
  localStorage.removeItem('user_first_name');
  localStorage.removeItem('user_full_name');
}

export async function register(data) {
  return request('/api/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function login(email, password) {
  return request('/api/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(refreshToken) {
  return request('/api/auth/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh: refreshToken }),
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
  });
}

export async function refreshAccessToken(refresh) {
  return request('/api/auth/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  });
}

export async function getProfile() {
  return request('/api/auth/profile/', {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
  });
}
