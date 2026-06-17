// Lists the family user's service requests in a flat table.
import { initFamilyPage } from '../js/app-shell.js';
import { getServiceRequests } from '../api/families.js';
import { renderRequestsTable, escapeHtml } from '../js/requests-table.js';

const container = document.getElementById('requests-container');

async function init() {
  const user = await initFamilyPage();
  if (!user) return;

  try {
    const requests = await getServiceRequests();
    renderRequestsTable(container, Array.isArray(requests) ? requests : requests.results || []);
  } catch (err) {
    container.innerHTML = `<p class="empty-message">${escapeHtml(
      err.message || 'Could not load your requests.'
    )}</p>`;
  }
}

init();
