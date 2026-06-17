// Shared rendering for a family's service requests, used by the dashboard
// ("My Requests" section) and the standalone my-requests page.

const CARE_TYPE_LABELS = {
  elderly_care: 'Elderly Care',
  childcare: 'Childcare',
  post_surgical: 'Post-Surgical Care',
  disability_support: 'Disability Support',
};

export function escapeHtml(value) {
  const div = document.createElement('div');
  div.textContent = value == null ? '' : String(value);
  return div.innerHTML;
}

function capitalize(value) {
  if (!value) return '';
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function careTypeLabel(value) {
  return CARE_TYPE_LABELS[value] || value;
}

export function renderRequestsTable(container, requests) {
  if (!requests.length) {
    container.innerHTML =
      '<p class="empty-message">You have not submitted any requests yet.</p>';
    return;
  }

  const rows = requests
    .map(
      (req) => `
        <tr>
          <td>${escapeHtml(careTypeLabel(req.care_type))}</td>
          <td>${escapeHtml(req.care_recipient_name)}</td>
          <td>${escapeHtml(req.location)}</td>
          <td>${escapeHtml(req.start_date)}</td>
          <td>${escapeHtml(req.end_date)}</td>
          <td>${escapeHtml(capitalize(req.status))}</td>
          <td><a class="text-link" href="service-request.html?id=${encodeURIComponent(req.id)}">View</a></td>
        </tr>`
    )
    .join('');

  container.innerHTML = `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Care Type</th>
            <th>Recipient</th>
            <th>Location</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}
