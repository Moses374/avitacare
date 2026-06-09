// ============================================================
// Avitacare — Frontend App
// ============================================================

const API_BASE = 'http://127.0.0.1:8000/api';

// ── Auth helpers ─────────────────────────────────────────────

function getToken() { return localStorage.getItem('access_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('user') || 'null'); }

function saveAuth(data) {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

function redirectByRole(role) {
  const routes = {
    caregiver: '/caregiver/dashboard.html',
    family:    '/family/dashboard.html',
    admin:     '/admin/dashboard.html',
  };
  window.location.href = routes[role] || '/';
}

// ── API client ───────────────────────────────────────────────

async function apiFetch(endpoint, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    clearAuth();
    window.location.href = '/login.html';
    return;
  }

  return res.ok ? res.json() : Promise.reject(await res.json());
}

// ── Auth actions ─────────────────────────────────────────────

async function login(email, password) {
  const data = await apiFetch('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  saveAuth(data);
  const user = await apiFetch('/users/me/');
  localStorage.setItem('user', JSON.stringify(user));
  redirectByRole(user.role);
}

async function register(payload) {
  await apiFetch('/users/register/', { method: 'POST', body: JSON.stringify(payload) });
  return login(payload.email, payload.password);
}

function logout() {
  clearAuth();
  window.location.href = '/login.html';
}

// ── UI helpers ───────────────────────────────────────────────

function showError(containerId, message) {
  const el = document.getElementById(containerId);
  if (el) { el.textContent = message; el.style.display = 'block'; }
}

function hideError(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.style.display = 'none';
}

// Guard: redirect unauthenticated users to login
function requireAuth() {
  if (!getToken()) window.location.href = '/login.html';
}
