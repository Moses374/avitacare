// ============================================================
// Avitacare, Frontend application core
// ============================================================

const API_BASE = '/api';

// ---------------- Auth helpers ----------------

function getToken() { return localStorage.getItem('access_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('user') || 'null'); }

function saveAuth(data) {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('user', JSON.stringify(data.user));
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
    admin:     '/admin/',
  };
  window.location.href = routes[role] || '/';
}

function requireAuth() {
  if (!getToken()) window.location.href = '/login.html';
}

// ---------------- API client ----------------

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

  if (!res.ok) {
    let body = {};
    try { body = await res.json(); } catch (e) { /* no body */ }
    throw body;
  }
  if (res.status === 204) return null;
  return res.json();
}

// ---------------- Auth actions ----------------

async function login(email, password) {
  const data = await apiFetch('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  saveAuth(data);
  redirectByRole(data.user.role);
}

async function register(payload) {
  const data = await apiFetch('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  saveAuth(data);
  redirectByRole(data.user.role);
}

async function logout() {
  const refresh = localStorage.getItem('refresh_token');
  try {
    await apiFetch('/auth/logout/', { method: 'POST', body: JSON.stringify({ refresh }) });
  } catch (e) {
    // ignore, clear local session regardless
  }
  clearAuth();
  window.location.href = '/login.html';
}

// ---------------- Error helpers ----------------

function formatApiError(err) {
  if (!err || typeof err !== 'object') return 'Something went wrong. Please try again.';
  if (err.detail) return err.detail;
  const parts = [];
  for (const key of Object.keys(err)) {
    const value = Array.isArray(err[key]) ? err[key].join(' ') : String(err[key]);
    parts.push(key === 'non_field_errors' ? value : `${key}: ${value}`);
  }
  return parts.join(' ') || 'Something went wrong. Please try again.';
}

function showError(containerId, message) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!el.querySelector('[data-icon], .icon')) {
    el.innerHTML = '<span data-icon="alert-circle" data-size="15"></span><span data-error-text></span>';
  }
  const textEl = el.querySelector('[data-error-text]') || el;
  textEl.textContent = message;
  el.style.display = 'flex';
  renderIcons(el);
}

function hideError(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.style.display = 'none';
}

// ---------------- Toasts ----------------

function ensureToastStack() {
  let stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }
  return stack;
}

function toast(message, type = 'info') {
  const stack = ensureToastStack();
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'alert-circle';
  el.innerHTML = `<span data-icon="${iconName}" data-size="16"></span><span>${message}</span>`;
  stack.appendChild(el);
  renderIcons(el);
  setTimeout(() => el.remove(), 4000);
}

// ---------------- Modal ----------------

function openModal(html) {
  let overlay = document.getElementById('app-modal');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'app-modal';
    overlay.className = 'modal-overlay hidden';
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
  }
  overlay.innerHTML = `<div class="modal">${html}</div>`;
  overlay.classList.remove('hidden');
  renderIcons(overlay);
}

function closeModal() {
  const overlay = document.getElementById('app-modal');
  if (overlay) overlay.classList.add('hidden');
}

function confirmDialog({ title, message, confirmLabel = 'Confirm', danger = false, onConfirm }) {
  openModal(`
    <div class="modal-header"><h2>${title}</h2>
      <button class="icon-btn" data-action="close"><span data-icon="x" data-size="16"></span></button>
    </div>
    <div class="modal-body"><p>${message}</p></div>
    <div class="modal-footer">
      <button class="btn" data-action="close">Cancel</button>
      <button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" id="modal-confirm-btn">${confirmLabel}</button>
    </div>
  `);
  const overlay = document.getElementById('app-modal');
  overlay.querySelectorAll('[data-action="close"]').forEach((btn) => btn.addEventListener('click', closeModal));
  document.getElementById('modal-confirm-btn').addEventListener('click', async () => {
    closeModal();
    await onConfirm();
  });
}

// ---------------- Empty / loading states ----------------

function loadingState(message = 'Loading...') {
  return `<div class="loading-block"><span data-icon="loader" data-size="22" class="spinner"></span><div class="loading-title">${message}</div></div>`;
}

function emptyState(title, sub = '', iconName = 'inbox') {
  return `<div class="empty-block"><span data-icon="${iconName}" data-size="28"></span><div class="empty-title">${title}</div>${sub ? `<div class="empty-sub">${sub}</div>` : ''}</div>`;
}

function renderInto(elOrId, html) {
  const el = typeof elOrId === 'string' ? document.getElementById(elOrId) : elOrId;
  if (!el) return;
  el.innerHTML = html;
  renderIcons(el);
}

// ---------------- Table renderer ----------------

function renderTable(elOrId, { columns, rows, rowKey, emptyTitle = 'No records found.', emptySub = '', emptyIcon = 'inbox' }) {
  if (!rows || rows.length === 0) {
    renderInto(elOrId, emptyState(emptyTitle, emptySub, emptyIcon));
    return;
  }
  const thead = `<thead><tr>${columns.map((c) => `<th>${c.header}</th>`).join('')}</tr></thead>`;
  const tbody = `<tbody>${rows.map((row) => `<tr>${columns.map((c) => `<td data-label="${c.header}">${c.render(row)}</td>`).join('')}</tr>`).join('')}</tbody>`;
  renderInto(elOrId, `<div class="table-wrap"><table class="data-table">${thead}${tbody}</table></div>`);
}

// ---------------- Status badge helper ----------------

const STATUS_ICONS = {
  pending: 'clock', open: 'clock', confirmed: 'check-circle', ongoing: 'clock',
  completed: 'check-circle', verified: 'check-circle', cancelled: 'x-circle',
  rejected: 'x-circle', matched: 'check-circle', closed: 'check-circle',
};
const STATUS_CLASS = {
  pending: 'status-warning', open: 'status-warning', confirmed: 'status-info', ongoing: 'status-info',
  completed: 'status-success', verified: 'status-success', cancelled: 'status-danger',
  rejected: 'status-danger', matched: 'status-info', closed: 'status-muted',
};

function statusLabel(value) {
  const icon = STATUS_ICONS[value] || 'alert-circle';
  const cls = STATUS_CLASS[value] || 'status-muted';
  const text = value ? value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, ' ') : 'Unknown';
  return `<span class="status ${cls}"><span data-icon="${icon}" data-size="14"></span>${text}</span>`;
}

// ---------------- App shell (sidebar + topbar) ----------------

const NAV_CONFIG = {
  family: [
    { label: 'Dashboard', href: '/family/dashboard.html', icon: 'home' },
    { label: 'Profile', href: '/family/profile.html', icon: 'user' },
    { label: 'Requests', href: '/family/requests.html', icon: 'clipboard' },
    { label: 'Bookings', href: '/family/bookings.html', icon: 'calendar' },
    { label: 'Reviews', href: '/family/reviews.html', icon: 'star' },
    { label: 'Notifications', href: '/family/notifications.html', icon: 'bell' },
    { label: 'Settings', href: '/family/settings.html', icon: 'settings' },
  ],
  caregiver: [
    { label: 'Dashboard', href: '/caregiver/dashboard.html', icon: 'home' },
    { label: 'Profile', href: '/caregiver/profile.html', icon: 'user' },
    { label: 'Bookings', href: '/caregiver/bookings.html', icon: 'calendar' },
    { label: 'Reviews', href: '/caregiver/reviews.html', icon: 'star' },
    { label: 'Notifications', href: '/caregiver/notifications.html', icon: 'bell' },
    { label: 'Settings', href: '/caregiver/settings.html', icon: 'settings' },
  ],
  admin: [
    { label: 'Dashboard', href: '/admin/', icon: 'home' },
    { label: 'Verifications', href: '/admin/verifications', icon: 'shield' },
    { label: 'Users', href: '/admin/users', icon: 'users' },
    { label: 'Audit Log', href: '/admin/audit-log', icon: 'file-text' },
    { label: 'Reports', href: '/admin/reports', icon: 'briefcase' },
    { label: 'Notifications', href: '/admin/notifications', icon: 'bell' },
    { label: 'Settings', href: '/admin/settings', icon: 'settings' },
  ],
};

function mountAppShell(pageTitle) {
  requireAuth();
  const user = getUser();
  if (!user) return;
  const items = NAV_CONFIG[user.role] || [];
  const path = window.location.pathname;

  const sidebarHtml = `
    <div class="brand"><img src="/static/logo-light.svg" alt="Avitacare" height="28" /></div>
    <nav>
      ${items.map((item) => `
        <a class="nav-item ${path === item.href ? 'active' : ''}" href="${item.href}">
          <span data-icon="${item.icon}" data-size="17"></span>${item.label}
        </a>`).join('')}
      <div class="nav-spacer"></div>
      <a class="nav-item" href="#" id="shell-logout"><span data-icon="log-out" data-size="17"></span>Log out</a>
    </nav>
  `;

  const notificationsHref = (items.find((i) => i.label === 'Notifications') || {}).href || '#';
  const topbarHtml = `
    <div class="page-title">${pageTitle}</div>
    <div class="topbar-actions">
      <a class="icon-btn" href="${notificationsHref}" id="shell-bell"><span data-icon="bell" data-size="17"></span></a>
      <div class="user-chip"><span data-icon="user" data-size="15"></span>${user.full_name || user.email}</div>
    </div>
  `;

  document.body.innerHTML = `
    <div class="app-shell">
      <aside class="sidebar">${sidebarHtml}</aside>
      <div class="main">
        <header class="topbar">${topbarHtml}</header>
        <main class="content" id="page-content"></main>
      </div>
    </div>
  `;

  document.getElementById('shell-logout').addEventListener('click', (e) => { e.preventDefault(); logout(); });
  renderIcons();
  pollUnreadNotifications();
}

// ---------------- Unread notifications badge ----------------

let unreadPollHandle = null;

async function refreshUnreadBadge() {
  const bell = document.getElementById('shell-bell');
  if (!bell) return;
  try {
    const notifications = await apiFetch('/notifications/');
    const unread = (notifications || []).filter((n) => !n.is_read).length;
    let badge = bell.querySelector('.notif-badge');
    if (unread > 0) {
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'notif-badge';
        bell.appendChild(badge);
      }
      badge.textContent = unread > 9 ? '9+' : String(unread);
    } else if (badge) {
      badge.remove();
    }
  } catch (e) {
    // Auth redirect or transient network error, skip this cycle.
  }
}

function pollUnreadNotifications() {
  refreshUnreadBadge();
  if (unreadPollHandle) clearInterval(unreadPollHandle);
  unreadPollHandle = setInterval(refreshUnreadBadge, 20000);
}
