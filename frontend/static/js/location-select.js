// ============================================================
// Avitacare, Location select
// Reusable Meilisearch-backed location autocomplete (county / sub-county).
// Usage:
//   1. Drop `locationSelectMarkup({ id, label, required, value })` into any
//      template string in place of a plain text location <input>.
//   2. After the markup is in the DOM, call `initLocationSelect(id, options)`
//      once to wire up search, keyboard nav, and selection.
//   3. Read the chosen location with `instance.getValue()`, which returns
//      null or { location_id, level, county, sub_county, display_name }.
// ============================================================

function debounce(fn, delay = 250) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function locationSelectMarkup({ id, label = '', required = false, placeholder = 'Search county or sub-county...', value = null }) {
  const hasValue = !!value;
  return `
    <div class="form-group location-select-group">
      ${label ? `<label for="${id}-input">${label}</label>` : ''}
      <div class="location-select" id="${id}">
        <div class="location-select-field">
          <input
            type="text"
            id="${id}-input"
            class="location-select-input"
            placeholder="${placeholder}"
            autocomplete="off"
            role="combobox"
            aria-expanded="false"
            aria-autocomplete="list"
            aria-controls="${id}-listbox"
            ${hasValue ? 'readonly' : ''}
            ${required ? 'required' : ''}
            value="${hasValue ? value.display_name : ''}"
          />
          <button type="button" class="location-select-clear ${hasValue ? '' : 'hidden'}" id="${id}-clear" aria-label="Clear location">
            <span data-icon="x" data-size="14"></span>
          </button>
        </div>
        <ul class="location-select-listbox hidden" id="${id}-listbox" role="listbox"></ul>
      </div>
    </div>
  `;
}

function initLocationSelect(id, { value = null, onChange = null } = {}) {
  const root = document.getElementById(id);
  if (!root) return null;

  const input = root.querySelector('.location-select-input');
  const clearBtn = root.querySelector('.location-select-clear');

  // Move listbox to body so it isn't clipped by any overflow container (e.g. modal).
  const listbox = root.querySelector('.location-select-listbox');
  document.body.appendChild(listbox);

  function positionListbox() {
    const rect = input.getBoundingClientRect();
    const width = Math.max(rect.width, 320);
    listbox.style.position = 'fixed';
    listbox.style.top  = (rect.bottom + 4) + 'px';
    listbox.style.left = rect.left + 'px';
    listbox.style.width = width + 'px';
    listbox.style.zIndex = '9999';
  }

  let results = [];
  let activeIndex = -1;
  let selected = value || null;

  function closeListbox() {
    listbox.classList.add('hidden');
    listbox.innerHTML = '';
    input.setAttribute('aria-expanded', 'false');
    activeIndex = -1;
  }

  function highlightActive() {
    const options = listbox.querySelectorAll('.location-select-option');
    options.forEach((el, i) => el.classList.toggle('is-active', i === activeIndex));
    if (options[activeIndex]) options[activeIndex].scrollIntoView({ block: 'nearest' });
  }

  function renderResults(items) {
    results = items;
    activeIndex = -1;
    positionListbox();
    if (!items.length) {
      listbox.innerHTML = '<li class="location-select-empty">No matching locations found.</li>';
      listbox.classList.remove('hidden');
      return;
    }
    listbox.innerHTML = items.map((item, i) => `
      <li role="option" class="location-select-option" data-index="${i}" id="${id}-opt-${i}">
        <span data-icon="map-pin" data-size="13"></span>
        <span class="location-select-option-label">${item.highlighted || item.display_name}</span>
        <span class="location-select-option-level">${item.level === 'county' ? 'County' : 'Sub-county'}</span>
      </li>
    `).join('');
    listbox.classList.remove('hidden');
    input.setAttribute('aria-expanded', 'true');
    listbox.querySelectorAll('.location-select-option').forEach((el) => {
      el.addEventListener('mousedown', (e) => {
        e.preventDefault();
        setSelected(results[Number(el.getAttribute('data-index'))]);
      });
    });
    if (typeof renderIcons === 'function') renderIcons(listbox);
  }

  const runSearch = debounce(async (query) => {
    if (!query) { closeListbox(); return; }
    positionListbox();
    listbox.innerHTML = '<li class="location-select-loading">Searching...</li>';
    listbox.classList.remove('hidden');
    try {
      const data = await apiFetch(`/locations/search/?q=${encodeURIComponent(query)}`);
      renderResults(data.results || []);
    } catch (e) {
      listbox.innerHTML = '<li class="location-select-error">Search is unavailable right now.</li>';
      listbox.classList.remove('hidden');
    }
  }, 300);

  function setSelected(location) {
    selected = location || null;
    if (selected) {
      input.value = selected.display_name;
      input.readOnly = true;
      root.classList.add('is-locked');
      clearBtn.classList.remove('hidden');
    } else {
      input.value = '';
      input.readOnly = false;
      root.classList.remove('is-locked');
      clearBtn.classList.add('hidden');
    }
    closeListbox();
    if (onChange) onChange(selected);
  }

  input.addEventListener('input', () => {
    if (selected) return;
    runSearch(input.value.trim());
  });

  input.addEventListener('keydown', (e) => {
    if (listbox.classList.contains('hidden')) return;
    const optionCount = results.length;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, optionCount - 1);
      highlightActive();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
      highlightActive();
    } else if (e.key === 'Enter') {
      if (activeIndex >= 0 && results[activeIndex]) {
        e.preventDefault();
        setSelected(results[activeIndex]);
      }
    } else if (e.key === 'Escape') {
      closeListbox();
    }
  });

  clearBtn.addEventListener('click', () => {
    setSelected(null);
    input.focus();
  });

  document.addEventListener('click', (e) => {
    if (!root.contains(e.target) && !listbox.contains(e.target)) closeListbox();
  });

  // Reposition on scroll or resize so the listbox tracks the input.
  const reposition = () => { if (!listbox.classList.contains('hidden')) positionListbox(); };
  window.addEventListener('scroll', reposition, true);
  window.addEventListener('resize', reposition);

  function destroy() {
    closeListbox();
    if (listbox.parentNode) listbox.parentNode.removeChild(listbox);
    window.removeEventListener('scroll', reposition, true);
    window.removeEventListener('resize', reposition);
  }

  if (selected) setSelected(selected);

  return {
    getValue: () => selected,
    setValue: setSelected,
    destroy,
  };
}
