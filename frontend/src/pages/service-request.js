// New service request form. Family-only page.
import { initFamilyPage } from '../js/app-shell.js';
import { createServiceRequest } from '../api/families.js';

const FIELD_IDS = [
  'care_type',
  'care_recipient_name',
  'care_recipient_age',
  'location',
  'start_date',
  'end_date',
  'additional_notes',
];

const form = document.getElementById('request-form');
const errorBanner = document.getElementById('error-banner');
const successMessage = document.getElementById('success-message');
const submitButton = form.querySelector('button[type="submit"]');
const startInput = document.getElementById('start_date');
const endInput = document.getElementById('end_date');

// Today (local) as YYYY-MM-DD — the earliest selectable date.
const today = new Date().toLocaleDateString('en-CA');

function applyDateBounds() {
  startInput.min = today;
  endInput.min = startInput.value || today;
}
applyDateBounds();

// Keep the end date on or after the chosen start date.
startInput.addEventListener('change', () => {
  endInput.min = startInput.value || today;
  if (endInput.value && endInput.value < endInput.min) {
    endInput.value = '';
  }
});

function clearErrors() {
  FIELD_IDS.forEach((id) => {
    const el = document.getElementById(`err-${id}`);
    if (el) el.textContent = '';
  });
  errorBanner.textContent = '';
}

function showFieldErrors(errors) {
  Object.entries(errors).forEach(([field, messages]) => {
    const message = Array.isArray(messages) ? messages[0] : messages;
    const el = document.getElementById(`err-${field}`);
    if (el) {
      el.textContent = message;
    } else {
      errorBanner.textContent = message;
    }
  });
}

// Client-side date checks. Returns true when the dates are valid.
function validateDates() {
  let ok = true;
  if (startInput.value && startInput.value < today) {
    document.getElementById('err-start_date').textContent = 'Start date cannot be in the past.';
    ok = false;
  }
  if (startInput.value && endInput.value && endInput.value <= startInput.value) {
    document.getElementById('err-end_date').textContent = 'End date must be after the start date.';
    ok = false;
  }
  return ok;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearErrors();
  successMessage.hidden = true;

  if (!validateDates()) return;

  const payload = {
    care_type: document.getElementById('care_type').value,
    care_recipient_name: document.getElementById('care_recipient_name').value.trim(),
    care_recipient_age: document.getElementById('care_recipient_age').value,
    location: document.getElementById('location').value.trim(),
    start_date: startInput.value,
    end_date: endInput.value,
    additional_notes: document.getElementById('additional_notes').value.trim(),
  };

  submitButton.disabled = true;
  submitButton.textContent = 'Submitting...';
  try {
    await createServiceRequest(payload);
    form.reset();
    applyDateBounds();
    successMessage.hidden = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    if (err.data && typeof err.data === 'object') {
      showFieldErrors(err.data);
    } else {
      errorBanner.textContent = err.message || 'Could not submit your request. Please try again.';
    }
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Submit Request';
  }
});

// Auth/role guard and top-nav setup. Runs alongside the form — the submit
// handler above is attached synchronously so it always intercepts the submit.
initFamilyPage();
