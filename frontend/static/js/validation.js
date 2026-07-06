// ============================================================
// Avitacare, client-side validation schemas (Zod)
// Requires /static/js/vendor/zod.umd.js loaded first (window.Zod).
// Rules mirror the backend serializers; the server stays the
// source of truth, this layer just catches nonsense before it
// leaves the browser.
//
// Usage in a submit handler:
//   const check = validate(SomeSchema, payload);
//   if (!applyValidation(check, { banner: 'error-msg', fields: { phone_number: 'phone' } })) return;
//   await apiFetch(..., JSON.stringify(check.data));
//
// `fields` maps schema keys to input element ids when they differ;
// keys without a matching element fall back to the banner.
// ============================================================

const z = window.Zod.z;

// ---------------- Shared field fragments ----------------

const emailField = z.string().trim()
  .min(1, 'Email is required.')
  .max(254, 'Email is too long.')
  .email('Enter a valid email address.');

const passwordField = z.string()
  .min(8, 'Password must be at least 8 characters.')
  .max(128, 'Password is too long.');

const nameField = (label) => z.string().trim()
  .min(1, `${label} is required.`)
  .max(150, `${label} is too long.`)
  .regex(/^[\p{L}][\p{L}' -]*$/u, `${label} may only contain letters, spaces, hyphens and apostrophes.`);

// Kenyan mobile formats: +2547XXXXXXXX / +2541XXXXXXXX / 07XXXXXXXX / 01XXXXXXXX
const phoneField = z.string().trim()
  .regex(/^(\+254[17]\d{8}|0[17]\d{8})$/, 'Enter a valid Kenyan phone number, e.g. 0712345678, 0112345678 or +254712345678.')
  .or(z.literal(''));

// "YYYY-MM-DDTHH:MM" from <input type="datetime-local">
const dateTimeField = (label) => z.string()
  .min(1, `${label} is required.`)
  .regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/, `${label} must be a valid date and time.`)
  .refine((v) => !Number.isNaN(new Date(v).getTime()), `${label} must be a valid date and time.`);

const tagListField = (label) => z.array(
  z.string().trim()
    .min(2, `Each ${label} entry needs at least 2 characters.`)
    .max(80, `Each ${label} entry must be under 80 characters.`)
).max(20, `You can add at most 20 ${label} entries.`);

const CARE_TYPE_VALUES = ['elderly', 'child', 'disability', 'post_hospital', 'palliative'];

// Cross-field schedule sanity: end after start, duration between 1 hour and
// 180 days, start not in the past (1h grace) and at most a year ahead.
// Computed outside Zod's refine pipeline so these errors still show alongside
// other field errors (Zod skips object refinements when any field fails).
const MIN_DURATION_MS = 60 * 60 * 1000;
const MAX_DURATION_MS = 180 * 24 * 60 * 60 * 1000;
const MAX_LEAD_MS = 365 * 24 * 60 * 60 * 1000;

function scheduleIssues(d, startKey, endKey) {
  const start = new Date(d[startKey]).getTime();
  const end = new Date(d[endKey]).getTime();
  if (Number.isNaN(start) || Number.isNaN(end)) return []; // field-level rules already flagged it
  const issues = [];
  if (end <= start) {
    issues.push({ path: [endKey], message: 'End must be after the start.' });
  } else if (end - start < MIN_DURATION_MS) {
    issues.push({ path: [endKey], message: 'The schedule must cover at least 1 hour.' });
  } else if (end - start > MAX_DURATION_MS) {
    issues.push({ path: [endKey], message: 'The schedule cannot span more than 180 days.' });
  }
  if (start < Date.now() - 60 * 60 * 1000) {
    issues.push({ path: [startKey], message: 'Start cannot be in the past.' });
  } else if (start > Date.now() + MAX_LEAD_MS) {
    issues.push({ path: [startKey], message: 'Start cannot be more than a year ahead.' });
  }
  return issues;
}

// Wrap a schema so safeParse() also reports schedule issues, merged with any
// field-level issues rather than gated behind them.
const scheduleRules = (schema, startKey, endKey) => ({
  safeParse(data) {
    const base = schema.safeParse(data);
    const extra = data && typeof data === 'object' ? scheduleIssues(data, startKey, endKey) : [];
    if (extra.length === 0) return base;
    const issues = [...(base.success ? [] : base.error.issues), ...extra];
    return { success: false, error: { issues } };
  },
});

// ---------------- Auth ----------------

const LoginSchema = z.object({
  email: emailField,
  password: z.string().min(1, 'Password is required.'),
});

const RegisterSchema = z.object({
  first_name: nameField('First name'),
  last_name: nameField('Last name'),
  email: emailField,
  phone_number: phoneField,
  role: z.enum(['caregiver', 'family'], { errorMap: () => ({ message: 'Select whether you are a caregiver or a family.' }) }),
  password: passwordField,
  password_confirm: z.string().min(1, 'Please confirm your password.'),
}).refine((d) => d.password === d.password_confirm, {
  message: 'Passwords do not match.',
  path: ['password_confirm'],
});

const ChangePasswordSchema = z.object({
  old_password: z.string().min(1, 'Current password is required.'),
  new_password: passwordField,
  new_password_confirm: z.string().min(1, 'Please confirm your new password.'),
}).refine((d) => d.new_password === d.new_password_confirm, {
  message: 'New passwords do not match.',
  path: ['new_password_confirm'],
}).refine((d) => d.old_password !== d.new_password, {
  message: 'New password must be different from the current one.',
  path: ['new_password'],
});

// ---------------- Caregiver profile ----------------

const CaregiverProfileSchema = z.object({
  bio: z.string().trim().max(2000, 'Bio must be under 2000 characters.'),
  years_experience: z.number({ invalid_type_error: 'Years of experience must be a number.' })
    .int('Years of experience must be a whole number.')
    .min(0, 'Years of experience cannot be negative.')
    .max(60, 'Years of experience above 60 is not plausible — double-check the value.'),
  location_id: z.string().min(1).nullable(),
  skills: tagListField('skill'),
  certifications: tagListField('certification'),
  is_available: z.boolean(),
});

// Register step 2 is the same minus location/availability.
const CaregiverApplicationSchema = CaregiverProfileSchema.pick({
  bio: true, years_experience: true, skills: true, certifications: true,
});

const ALLOWED_DOC_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png'];
const MAX_DOC_MB = 5;

const DocumentUploadSchema = z.object({
  label: z.string().trim().min(1, 'Document label is required.').max(150, 'Document label is too long.'),
  file: z.custom((f) => f instanceof File, { message: 'Please choose a file.' })
    .refine((f) => ALLOWED_DOC_EXTENSIONS.includes((f.name.split('.').pop() || '').toLowerCase()),
      `File must be one of: ${ALLOWED_DOC_EXTENSIONS.join(', ')}.`)
    .refine((f) => f.size > 0, 'File is empty.')
    .refine((f) => f.size <= MAX_DOC_MB * 1024 * 1024, `File must be under ${MAX_DOC_MB} MB.`),
});

// ---------------- Family profile ----------------

const FamilyProfileSchema = z.object({
  location_id: z.string().min(1).nullable(),
  preferred_caregiver_type: z.enum(['', ...CARE_TYPE_VALUES], { errorMap: () => ({ message: 'Choose a valid caregiver type.' }) }),
  care_recipient_name: z.string().trim().max(150, 'Care recipient name is too long.')
    .refine((v) => v === '' || /^[\p{L}][\p{L}' -]*$/u.test(v), 'Care recipient name may only contain letters, spaces, hyphens and apostrophes.'),
  care_recipient_details: z.string().trim().max(2000, 'Care recipient details must be under 2000 characters.'),
});

// ---------------- Service requests & bookings ----------------

const ServiceRequestSchema = scheduleRules(z.object({
  care_type: z.enum(CARE_TYPE_VALUES, { errorMap: () => ({ message: 'Choose a valid care type.' }) }),
  description: z.string().trim()
    .min(10, 'Description must be at least 10 characters — describe the care you need.')
    .max(2000, 'Description must be under 2000 characters.'),
  location_id: z.string({ invalid_type_error: 'Please select a location from the suggestions.' })
    .min(1, 'Please select a location from the suggestions.'),
  urgency_level: z.enum(['low', 'medium', 'high'], { errorMap: () => ({ message: 'Choose a valid urgency level.' }) }),
  required_skills: tagListField('skill'),
  schedule_start: dateTimeField('Start'),
  schedule_end: dateTimeField('End'),
}), 'schedule_start', 'schedule_end');

// Booking dates are not collected here: the API reuses the schedule the
// family already set on the service request.
const BookingSchema = z.object({
  caregiver: z.number().int().positive('Caregiver is missing.'),
  service_request: z.number().int().positive('Service request is missing.'),
  notes: z.string().trim().max(1000, 'Notes must be under 1000 characters.'),
});

// ---------------- Reviews ----------------

const ReviewSchema = z.object({
  booking: z.number().int().positive('Booking is missing.'),
  rating: z.number({ invalid_type_error: 'Rating must be a number.' })
    .int('Rating must be a whole number.')
    .min(1, 'Rating must be between 1 and 5.')
    .max(5, 'Rating must be between 1 and 5.'),
  comment: z.string().trim().max(1000, 'Comment must be under 1000 characters.'),
});

// ---------------- Helpers ----------------

// Parse `data` with `schema`. On success returns { ok: true, data } with
// Zod's trimmed/coerced output (use it as the request payload). On failure
// returns { ok: false, fieldErrors, message }:
//   fieldErrors — first message per top-level field, keyed by schema field name
//   message     — the first few distinct problems joined, for banner fallback
function validate(schema, data) {
  const result = schema.safeParse(data);
  if (result.success) return { ok: true, data: result.data };
  const fieldErrors = {};
  for (const issue of result.error.issues) {
    const key = issue.path.length ? String(issue.path[0]) : '_form';
    if (!(key in fieldErrors)) fieldErrors[key] = issue.message;
  }
  const messages = [...new Set(result.error.issues.map((i) => i.message))];
  return { ok: false, fieldErrors, message: messages.slice(0, 3).join(' ') };
}

// Remove every inline error previously added by applyValidation.
function clearFieldErrors() {
  document.querySelectorAll('.field-error[data-auto]').forEach((el) => el.remove());
  document.querySelectorAll('.form-group.has-error').forEach((el) => el.classList.remove('has-error'));
}

// Show `message` under the field: mark its .form-group and append an inline
// error that clears itself as soon as the user edits the field.
function showFieldError(inputEl, message) {
  const group = inputEl.closest('.form-group') || inputEl.parentElement;
  if (!group) return false;
  group.classList.add('has-error');
  const el = document.createElement('div');
  el.className = 'field-error';
  el.setAttribute('data-auto', '');
  el.textContent = message;
  group.appendChild(el);
  const clear = () => { group.classList.remove('has-error'); el.remove(); };
  inputEl.addEventListener('input', clear, { once: true });
  inputEl.addEventListener('change', clear, { once: true });
  return true;
}

// Render a validate() result into the form. Returns true when valid.
// opts.fields maps schema keys to element ids when they differ from the key;
// errors that can't be placed next to a field go to opts.banner instead.
function applyValidation(check, { banner = null, fields = {} } = {}) {
  clearFieldErrors();
  if (banner) hideError(banner);
  if (check.ok) return true;

  const unplaced = [];
  for (const [key, message] of Object.entries(check.fieldErrors)) {
    const el = document.getElementById(fields[key] || key);
    if (!el || !showFieldError(el, message)) unplaced.push(message);
  }
  if (unplaced.length && banner) showError(banner, unplaced.join(' '));

  const firstInvalid = document.querySelector('.form-group.has-error input, .form-group.has-error select, .form-group.has-error textarea');
  if (firstInvalid) firstInvalid.focus();
  return false;
}
