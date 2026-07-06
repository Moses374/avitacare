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

// ---------------- WhatsApp contact reveal ----------------
// Phone numbers are only present on a booking once the caregiver has
// accepted it (confirmed/ongoing/completed) — the API hides them before that.

// "+254712345678" / "0712345678" → "254712345678" (wa.me format), or null.
function waNumber(phone) {
  const digits = String(phone || '').replace(/[\s()-]/g, '');
  if (/^\+254[17]\d{8}$/.test(digits)) return digits.slice(1);
  if (/^0[17]\d{8}$/.test(digits)) return '254' + digits.slice(1);
  if (/^254[17]\d{8}$/.test(digits)) return digits;
  return null;
}

// "254712345678" → "+254 712 345 678" for display.
function waPretty(number) {
  return `+${number.slice(0, 3)} ${number.slice(3, 6)} ${number.slice(6, 9)} ${number.slice(9)}`;
}

const WHATSAPP_GLYPH = '<svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.52.149-.174.198-.298.297-.497.1-.198.05-.371-.025-.52-.074-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>';

// Counterpart contact + a fitting opener for whichever side is viewing.
function waContactFor(booking, viewerRole) {
  const start = new Date(booking.scheduled_start).toLocaleString(undefined, {
    weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit',
  });
  const me = (getUser() || {}).full_name || 'an AvitaCare member';
  if (viewerRole === 'family') {
    const first = (booking.caregiver_name || 'there').split(' ')[0];
    return {
      name: booking.caregiver_name,
      phone: booking.caregiver_phone,
      message: `Hello ${first}, this is ${me} — we're matched on AvitaCare for the booking starting ${start}. I'd love to coordinate the final details with you. Thank you!`,
    };
  }
  const first = (booking.family_name || 'there').split(' ')[0];
  return {
    name: booking.family_name,
    phone: booking.family_phone,
    message: `Hello ${first}, this is ${me}, your AvitaCare caregiver for the booking starting ${start}. I'm looking forward to helping — feel free to share anything I should know beforehand.`,
  };
}

// Action-column button; empty string while the number is still hidden.
function waButton(booking, viewerRole) {
  const contact = waContactFor(booking, viewerRole);
  if (!waNumber(contact.phone)) return '';
  return `<button class="btn btn-sm btn-whatsapp" data-whatsapp="${booking.id}">${WHATSAPP_GLYPH}WhatsApp</button>`;
}

function openWhatsAppModal(booking, viewerRole) {
  const contact = waContactFor(booking, viewerRole);
  const number = waNumber(contact.phone);
  if (!number) return;
  const initials = (contact.name || '?').split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase();

  openModal(`
    <div class="modal-header"><h2>Chat on WhatsApp</h2>
      <button class="icon-btn" data-action="close"><span data-icon="x" data-size="16"></span></button>
    </div>
    <div class="modal-body">
      <div class="wa-contact">
        <div class="wa-avatar">${initials}</div>
        <div class="wa-contact-details">
          <div class="wa-name">${contact.name}</div>
          <div class="wa-phone">${WHATSAPP_GLYPH}${waPretty(number)}</div>
        </div>
      </div>
      <div class="form-group">
        <label for="wa-message">Your message</label>
        <textarea id="wa-message" rows="4">${contact.message}</textarea>
        <p class="field-hint">WhatsApp opens with this message pre-filled — tweak it here or before sending.</p>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn" data-action="close">Cancel</button>
      <button class="btn btn-whatsapp" id="wa-open-btn">${WHATSAPP_GLYPH}Open WhatsApp</button>
    </div>
  `);
  document.querySelectorAll('[data-action="close"]').forEach((btn) => btn.addEventListener('click', closeModal));
  document.getElementById('wa-open-btn').addEventListener('click', () => {
    const text = document.getElementById('wa-message').value.trim();
    window.open(`https://wa.me/${number}?text=${encodeURIComponent(text)}`, '_blank', 'noopener');
    closeModal();
  });
}

// Attach modal openers to every [data-whatsapp] button in the table.
function wireWhatsAppButtons(bookings, viewerRole) {
  document.querySelectorAll('[data-whatsapp]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = Number(btn.getAttribute('data-whatsapp'));
      openWhatsAppModal(bookings.find((b) => b.id === id), viewerRole);
    });
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
    <div class="brand"><img src="/static/avitacareicon.png" alt="" height="30" /><span>Avitacare</span></div>
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
