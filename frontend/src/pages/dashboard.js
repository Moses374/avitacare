// Role-aware dashboard. Loads the current user, renders their section links,
// and shows the active section's content in #main-content.
import { getProfile, clearTokens } from '../api/auth.js';
import { getServiceRequests } from '../api/families.js';
import { requireAuth, initSignOut, setNavUser } from '../js/app-shell.js';
import { renderRequestsTable, escapeHtml } from '../js/requests-table.js';

function comingSoon(content) {
  content.innerHTML = '<p class="content-message">This section is coming soon.</p>';
}

// Renders the family's service requests inline, with a link to create a new one.
async function renderMyRequests(content) {
  content.innerHTML = `
    <div class="toolbar">
      <a class="text-link" href="service-request.html">Submit a new request</a>
    </div>
    <div id="requests-container">
      <p class="empty-message">Loading your requests...</p>
    </div>`;

  const container = document.getElementById('requests-container');
  try {
    const requests = await getServiceRequests();
    renderRequestsTable(container, Array.isArray(requests) ? requests : requests.results || []);
  } catch (err) {
    container.innerHTML = `<p class="empty-message">${escapeHtml(
      err.message || 'Could not load your requests.'
    )}</p>`;
  }
}

// Section links per role. A section either renders content or is a placeholder.
const ROLE_NAV = {
  family: [
    { label: 'My Requests', render: renderMyRequests },
    { label: 'Find a Caregiver' },
    { label: 'My Bookings' },
  ],
  caregiver: [
    { label: 'My Profile' },
    { label: 'Available Requests' },
    { label: 'My Bookings' },
  ],
  admin: [
    { label: 'Users' },
    { label: 'Caregiver Verification' },
    { label: 'All Bookings' },
    { label: 'Reviews' },
  ],
};

function capitalize(value) {
  if (!value) return '';
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function fullName(user) {
  return user.full_name || `${user.first_name} ${user.last_name}`.trim();
}

function renderRoleNav(role) {
  const nav = document.getElementById('role-nav');
  const content = document.getElementById('main-content');
  const sections = ROLE_NAV[role] || [];

  function activate(link, section) {
    nav.querySelectorAll('a').forEach((a) => a.classList.remove('active'));
    link.classList.add('active');
    if (section.render) {
      section.render(content);
    } else {
      comingSoon(content);
    }
  }

  sections.forEach((section, index) => {
    const link = document.createElement('a');
    link.textContent = section.label;
    link.href = '#';
    link.addEventListener('click', (event) => {
      event.preventDefault();
      activate(link, section);
    });
    nav.appendChild(link);

    // The first section is active (and rendered) as soon as the page loads.
    if (index === 0) activate(link, section);
  });
}

async function init() {
  if (!requireAuth()) return;
  initSignOut();

  let user;
  try {
    user = await getProfile();
  } catch {
    clearTokens();
    window.location.replace('login.html');
    return;
  }

  localStorage.setItem('user_role', user.role);
  setNavUser(fullName(user));

  document.getElementById('welcome-heading').textContent = `Welcome back, ${user.first_name}.`;
  document.getElementById('role-subheading').textContent =
    `You are signed in as a ${capitalize(user.role)}.`;

  renderRoleNav(user.role);
}

init();
