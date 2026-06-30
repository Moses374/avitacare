// ============================================================
// Avitacare, Icon system
// Vanilla-JS, Lucide-style line icons (no React, no external CDN).
// Usage: <span data-icon="bell" data-size="18"></span> then call renderIcons().
// ============================================================

const ICONS = {
  'home': '<path d="M3 9.5 12 3l9 6.5"/><path d="M5 10v10a1 1 0 0 0 1 1h3v-6h6v6h3a1 1 0 0 0 1-1V10"/>',
  'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-3.9 3.6-7 8-7s8 3.1 8 7"/>',
  'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 21c0-3.6 2.9-6.5 6.5-6.5s6.5 2.9 6.5 6.5"/><path d="M16.5 5.5a3.5 3.5 0 0 1 0 7"/><path d="M21.5 21c0-3-2-5.6-5-6.3"/>',
  'bell': '<path d="M6 9a6 6 0 0 1 12 0c0 4 1.5 6 2 7H4c.5-1 2-3 2-7"/><path d="M9.5 19a2.5 2.5 0 0 0 5 0"/>',
  'calendar': '<rect x="3.5" y="5" width="17" height="16" rx="2"/><path d="M3.5 9.5h17"/><path d="M8 3v4"/><path d="M16 3v4"/>',
  'clipboard': '<rect x="5" y="4.5" width="14" height="17" rx="2"/><rect x="9" y="2.5" width="6" height="3" rx="1"/><path d="M8.5 10h7"/><path d="M8.5 14h7"/><path d="M8.5 18h4.5"/>',
  'shield': '<path d="M12 3.5 19 6v6c0 5-3 7.7-7 8.5-4-.8-7-3.5-7-8.5V6Z"/>',
  'star': '<path d="M12 3.5 14.6 9l6 .9-4.3 4.2 1 6-5.3-2.8-5.3 2.8 1-6L3.4 9.9l6-.9Z"/>',
  'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M19.5 19.5 15.4 15.4"/>',
  'settings': '<circle cx="12" cy="12" r="3"/><path d="M19.4 13.5a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V19.5a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H4.5a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H10.6a1.7 1.7 0 0 0 1-1.5V4.5a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V10.6a1.7 1.7 0 0 0 1.5 1H19.5a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.6 1Z"/>',
  'check-circle': '<circle cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.2 2.2 4.8-5"/>',
  'x-circle': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5l5 5"/><path d="M14.5 9.5l-5 5"/>',
  'alert-triangle': '<path d="M12 4 21.5 20H2.5Z"/><path d="M12 10v4"/><path d="M12 17.2v.1"/>',
  'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
  'file-text': '<path d="M7 3.5h7l3.5 3.5V20a.5.5 0 0 1-.5.5H7a.5.5 0 0 1-.5-.5V4a.5.5 0 0 1 .5-.5Z"/><path d="M14 3.5V7h3.5"/><path d="M9 12h6"/><path d="M9 15.5h6"/><path d="M9 8.5h2"/>',
  'message-square': '<path d="M4 4.5h16v12H9l-4 4v-4H4Z"/>',
  'upload': '<path d="M12 16V4"/><path d="M7.5 8.5 12 4l4.5 4.5"/><path d="M5 16v3a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3"/>',
  'log-out': '<path d="M9 21H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>',
  'plus': '<path d="M12 5v14"/><path d="M5 12h14"/>',
  'x': '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
  'chevron-left': '<path d="M15 5 8 12l7 7"/>',
  'chevron-right': '<path d="M9 5l7 7-7 7"/>',
  'chevron-down': '<path d="M5 9l7 7 7-7"/>',
  'filter': '<path d="M4 5h16l-6 7.5V19l-4 2v-8.5Z"/>',
  'more-horizontal': '<circle cx="5" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="19" cy="12" r="1.4"/>',
  'eye': '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="3"/>',
  'check': '<path d="M5 12.5 9.5 17 19 6.5"/>',
  'loader': '<path d="M12 3v3.5"/><path d="M12 17.5V21"/><path d="M5.6 5.6l2.5 2.5"/><path d="M15.9 15.9l2.5 2.5"/><path d="M3 12h3.5"/><path d="M17.5 12H21"/><path d="M5.6 18.4l2.5-2.5"/><path d="M15.9 8.1l2.5-2.5"/>',
  'menu': '<path d="M4 6.5h16"/><path d="M4 12h16"/><path d="M4 17.5h16"/>',
  'arrow-left': '<path d="M19 12H5"/><path d="M11 5l-7 7 7 7"/>',
  'trash': '<path d="M4.5 7h15"/><path d="M9.5 7V4.5a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1V7"/><path d="M6.5 7l1 12.5a1 1 0 0 0 1 .9h7a1 1 0 0 0 1-.9L17.5 7"/>',
  'edit': '<path d="M4 20h4.5L19 9.5a2.4 2.4 0 0 0-3.4-3.4L5 16.5Z"/>',
  'map-pin': '<path d="M12 21s7-6.3 7-11.5a7 7 0 1 0-14 0C5 14.7 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
  'briefcase': '<rect x="3" y="7.5" width="18" height="12" rx="2"/><path d="M8 7.5V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1.5"/><path d="M3 12.5h18"/>',
  'award': '<circle cx="12" cy="8.5" r="5"/><path d="M9 13l-1.5 7L12 18l4.5 2-1.5-7"/>',
  'download': '<path d="M12 4v12"/><path d="M7.5 11.5 12 16l4.5-4.5"/><path d="M5 19h14"/>',
  'refresh': '<path d="M4 12a8 8 0 0 1 14-5.3L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-14 5.3L4 16"/><path d="M4 20v-4h4"/>',
  'inbox': '<path d="M4 12.5h4l2 3h4l2-3h4"/><path d="M5.5 5h13l2.5 7.5V18a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-5.5Z"/>',
  'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v6"/><path d="M12 16.5v.1"/>',
};

function renderIcons(root) {
  const scope = root || document;
  scope.querySelectorAll('[data-icon]').forEach((el) => {
    const name = el.getAttribute('data-icon');
    const size = el.getAttribute('data-size') || '18';
    const inner = ICONS[name];
    if (!inner) return;
    el.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`;
    el.classList.add('icon');
    el.removeAttribute('data-icon');
  });
}

document.addEventListener('DOMContentLoaded', () => renderIcons());
