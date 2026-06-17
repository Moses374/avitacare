// Family API client — talks to the Django backend.
// Every request carries the JWT access token from localStorage.
import { API_BASE } from './config.js';

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
  };
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message =
      data.detail ||
      Object.values(data).flat().join(' ') ||
      'Request failed.';
    const err = new Error(message);
    err.data = data;
    err.status = res.status;
    throw err;
  }
  return data;
}

export function getFamilyProfile() {
  return request('/api/families/profile/');
}

export function updateFamilyProfile(data) {
  return request('/api/families/profile/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export function getServiceRequests() {
  return request('/api/families/requests/');
}

export function createServiceRequest(data) {
  return request('/api/families/requests/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getServiceRequest(id) {
  return request(`/api/families/requests/${id}/`);
}

export function updateServiceRequest(id, data) {
  return request(`/api/families/requests/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export function deleteServiceRequest(id) {
  return request(`/api/families/requests/${id}/`, {
    method: 'DELETE',
  });
}
