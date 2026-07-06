// ============================================================
// Avitacare, validation schema tests
// Run with:  node frontend/tests/validation.test.js
// No dependencies — loads the vendored Zod UMD build and
// validation.js exactly as the browser does.
// ============================================================

const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..', '..');

// In a browser the UMD attaches window.Zod; under require() it exports CJS, so bridge it.
global.window = global;
global.window.Zod = require(path.join(root, 'frontend/static/js/vendor/zod.umd.js'));

// Minimal stub for the File type used by DocumentUploadSchema.
global.File = class File { constructor(name, size) { this.name = name; this.size = size; } };

// const → var so the schema bindings escape eval() into this module's scope.
eval(fs.readFileSync(path.join(root, 'frontend/static/js/validation.js'), 'utf8').replace(/^const /gm, 'var '));

let pass = 0, fail = 0;

// Positive case: expects ok. Negative case: expects a rejection whose message
// contains `msgContains`, attributed to field `onField` (when given).
function expect(label, result, shouldBeOk, msgContains, onField) {
  const problems = [];
  if (result.ok !== shouldBeOk) problems.push(`expected ok=${shouldBeOk}, got ${result.ok}`);
  if (!shouldBeOk && result.ok === false) {
    if (msgContains && !(result.message || '').toLowerCase().includes(msgContains.toLowerCase())) {
      problems.push(`message "${result.message}" missing "${msgContains}"`);
    }
    if (onField && !(onField in (result.fieldErrors || {}))) {
      problems.push(`error not attributed to field "${onField}" (got: ${Object.keys(result.fieldErrors || {}).join(', ')})`);
    }
  }
  if (problems.length) { fail++; console.log(`FAIL ${label}: ${problems.join('; ')}`); }
  else pass++;
}

// datetime-local string N days from now at hour h
const dt = (days, h = 9, min = 0) => {
  const d = new Date(Date.now() + days * 864e5);
  d.setHours(h, min, 0, 0);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
};

// ---------------- Login ----------------
expect('login: valid', validate(LoginSchema, { email: 'a@b.co', password: 'x' }), true);
expect('login: bad email', validate(LoginSchema, { email: 'not-an-email', password: 'x' }), false, 'valid email', 'email');
expect('login: empty email', validate(LoginSchema, { email: '', password: 'x' }), false, 'Email is required', 'email');
expect('login: email too long', validate(LoginSchema, { email: 'a'.repeat(250) + '@b.co', password: 'x' }), false, 'too long', 'email');
expect('login: empty password', validate(LoginSchema, { email: 'a@b.co', password: '' }), false, 'Password is required', 'password');

// ---------------- Register ----------------
const reg = { first_name: 'Grace', last_name: 'Mwangi', email: 'g@x.com', phone_number: '+254712345678', role: 'family', password: 'Family1234!', password_confirm: 'Family1234!' };
expect('register: valid', validate(RegisterSchema, reg), true);
expect('register: valid 07 phone', validate(RegisterSchema, { ...reg, phone_number: '0712345678' }), true);
expect('register: valid 01 phone', validate(RegisterSchema, { ...reg, phone_number: '0112345678' }), true);
expect('register: empty phone ok', validate(RegisterSchema, { ...reg, phone_number: '' }), true);
expect('register: accented name ok', validate(RegisterSchema, { ...reg, first_name: 'Ngũgĩ' }), true);
expect('register: hyphenated name ok', validate(RegisterSchema, { ...reg, last_name: "O'Brien-Otieno" }), true);
expect('register: trims whitespace', (() => { const r = validate(RegisterSchema, { ...reg, first_name: '  Grace ' }); return { ok: r.ok && r.data.first_name === 'Grace' }; })(), true);
expect('register: phone too short', validate(RegisterSchema, { ...reg, phone_number: '07123' }), false, 'phone', 'phone_number');
expect('register: phone too long', validate(RegisterSchema, { ...reg, phone_number: '+25471234567890' }), false, 'phone', 'phone_number');
expect('register: phone wrong prefix', validate(RegisterSchema, { ...reg, phone_number: '0812345678' }), false, 'phone', 'phone_number');
expect('register: phone letters', validate(RegisterSchema, { ...reg, phone_number: '07one2345678' }), false, 'phone', 'phone_number');
expect('register: empty first name', validate(RegisterSchema, { ...reg, first_name: '' }), false, 'First name is required', 'first_name');
expect('register: digits in name', validate(RegisterSchema, { ...reg, first_name: 'Grace99' }), false, 'letters', 'first_name');
expect('register: symbol name', validate(RegisterSchema, { ...reg, last_name: '<script>' }), false, 'letters', 'last_name');
expect('register: name too long', validate(RegisterSchema, { ...reg, first_name: 'A'.repeat(151) }), false, 'too long', 'first_name');
expect('register: role admin blocked', validate(RegisterSchema, { ...reg, role: 'admin' }), false, 'caregiver or a family', 'role');
expect('register: role empty', validate(RegisterSchema, { ...reg, role: '' }), false, 'caregiver or a family', 'role');
expect('register: password 7 chars', validate(RegisterSchema, { ...reg, password: 'Abcd123', password_confirm: 'Abcd123' }), false, 'at least 8', 'password');
expect('register: password 129 chars', validate(RegisterSchema, { ...reg, password: 'x'.repeat(129), password_confirm: 'x'.repeat(129) }), false, 'too long', 'password');
expect('register: password mismatch', validate(RegisterSchema, { ...reg, password_confirm: 'Different1!' }), false, 'do not match', 'password_confirm');
expect('register: confirm empty', validate(RegisterSchema, { ...reg, password_confirm: '' }), false, 'confirm', 'password_confirm');

// ---------------- Change password ----------------
const chpw = { old_password: 'OldPass1!', new_password: 'NewPass1!', new_password_confirm: 'NewPass1!' };
expect('chpw: valid', validate(ChangePasswordSchema, chpw), true);
expect('chpw: old empty', validate(ChangePasswordSchema, { ...chpw, old_password: '' }), false, 'Current password is required', 'old_password');
expect('chpw: new too short', validate(ChangePasswordSchema, { ...chpw, new_password: 'short1', new_password_confirm: 'short1' }), false, 'at least 8', 'new_password');
expect('chpw: mismatch', validate(ChangePasswordSchema, { ...chpw, new_password_confirm: 'Other123' }), false, 'do not match', 'new_password_confirm');
expect('chpw: same as old', validate(ChangePasswordSchema, { old_password: 'SamePass1', new_password: 'SamePass1', new_password_confirm: 'SamePass1' }), false, 'different', 'new_password');

// ---------------- Caregiver profile ----------------
const cg = { bio: 'Experienced caregiver.', years_experience: 5, location_id: 'KE-47', skills: ['elderly_care'], certifications: ['First Aid'], is_available: true };
expect('cg: valid', validate(CaregiverProfileSchema, cg), true);
expect('cg: zero years ok (starting out)', validate(CaregiverProfileSchema, { ...cg, years_experience: 0 }), true);
expect('cg: 60 years ok (boundary)', validate(CaregiverProfileSchema, { ...cg, years_experience: 60 }), true);
expect('cg: null location ok', validate(CaregiverProfileSchema, { ...cg, location_id: null }), true);
expect('cg: empty bio ok', validate(CaregiverProfileSchema, { ...cg, bio: '' }), true);
expect('cg: negative years', validate(CaregiverProfileSchema, { ...cg, years_experience: -1 }), false, 'negative', 'years_experience');
expect('cg: 61 years implausible', validate(CaregiverProfileSchema, { ...cg, years_experience: 61 }), false, 'not plausible', 'years_experience');
expect('cg: 130 years implausible', validate(CaregiverProfileSchema, { ...cg, years_experience: 130 }), false, 'not plausible', 'years_experience');
expect('cg: fractional years', validate(CaregiverProfileSchema, { ...cg, years_experience: 2.5 }), false, 'whole number', 'years_experience');
expect('cg: years NaN', validate(CaregiverProfileSchema, { ...cg, years_experience: NaN }), false, 'number', 'years_experience');
expect('cg: years as string', validate(CaregiverProfileSchema, { ...cg, years_experience: '5' }), false, 'number', 'years_experience');
expect('cg: bio over 2000', validate(CaregiverProfileSchema, { ...cg, bio: 'x'.repeat(2001) }), false, 'under 2000', 'bio');
expect('cg: 1-char skill', validate(CaregiverProfileSchema, { ...cg, skills: ['x'] }), false, '2 characters', 'skills');
expect('cg: 81-char skill', validate(CaregiverProfileSchema, { ...cg, skills: ['x'.repeat(81)] }), false, 'under 80', 'skills');
expect('cg: 21 skills', validate(CaregiverProfileSchema, { ...cg, skills: Array.from({ length: 21 }, (_, i) => `skill_${i}`) }), false, 'at most 20', 'skills');
expect('cg: availability not boolean', validate(CaregiverProfileSchema, { ...cg, is_available: 'yes' }), false, '', 'is_available');
expect('cg application: valid', validate(CaregiverApplicationSchema, { bio: 'Hi there', years_experience: 2, skills: [], certifications: [] }), true);
expect('cg application: implausible years', validate(CaregiverApplicationSchema, { bio: '', years_experience: 99, skills: [], certifications: [] }), false, 'not plausible', 'years_experience');

// ---------------- Document upload ----------------
expect('doc: valid pdf', validate(DocumentUploadSchema, { label: 'National ID', file: new File('id.pdf', 1024) }), true);
expect('doc: valid jpeg', validate(DocumentUploadSchema, { label: 'Cert', file: new File('c.JPEG', 1024) }), true);
expect('doc: 5MB boundary ok', validate(DocumentUploadSchema, { label: 'Scan', file: new File('s.png', 5 * 1024 * 1024) }), true);
expect('doc: no file', validate(DocumentUploadSchema, { label: 'ID', file: undefined }), false, 'choose a file', 'file');
expect('doc: exe blocked', validate(DocumentUploadSchema, { label: 'ID', file: new File('run.exe', 10) }), false, 'must be one of', 'file');
expect('doc: no extension', validate(DocumentUploadSchema, { label: 'ID', file: new File('mystery', 10) }), false, 'must be one of', 'file');
expect('doc: empty file', validate(DocumentUploadSchema, { label: 'ID', file: new File('id.pdf', 0) }), false, 'empty', 'file');
expect('doc: over 5MB', validate(DocumentUploadSchema, { label: 'ID', file: new File('big.pdf', 5 * 1024 * 1024 + 1) }), false, 'under 5', 'file');
expect('doc: blank label', validate(DocumentUploadSchema, { label: '   ', file: new File('id.pdf', 10) }), false, 'label is required', 'label');
expect('doc: label too long', validate(DocumentUploadSchema, { label: 'x'.repeat(151), file: new File('id.pdf', 10) }), false, 'too long', 'label');

// ---------------- Family profile ----------------
const fam = { location_id: 'KE-47', preferred_caregiver_type: 'elderly', care_recipient_name: 'Jane Doe', care_recipient_details: 'Mobility help needed.' };
expect('family: valid', validate(FamilyProfileSchema, fam), true);
expect('family: all optional empty ok', validate(FamilyProfileSchema, { location_id: null, preferred_caregiver_type: '', care_recipient_name: '', care_recipient_details: '' }), true);
expect('family: bad care type', validate(FamilyProfileSchema, { ...fam, preferred_caregiver_type: 'robot' }), false, 'valid caregiver type', 'preferred_caregiver_type');
expect('family: digits in recipient name', validate(FamilyProfileSchema, { ...fam, care_recipient_name: 'Jane99' }), false, 'letters', 'care_recipient_name');
expect('family: recipient name too long', validate(FamilyProfileSchema, { ...fam, care_recipient_name: 'A'.repeat(151) }), false, 'too long', 'care_recipient_name');
expect('family: details over 2000', validate(FamilyProfileSchema, { ...fam, care_recipient_details: 'x'.repeat(2001) }), false, 'under 2000', 'care_recipient_details');

// ---------------- Service request ----------------
const sr = { care_type: 'elderly', description: 'Daily support for my mother with mobility help.', location_id: 'KE-47-WESTLANDS', urgency_level: 'medium', required_skills: ['elderly_care'], schedule_start: dt(2), schedule_end: dt(2, 17) };
expect('request: valid', validate(ServiceRequestSchema, sr), true);
expect('request: no skills ok', validate(ServiceRequestSchema, { ...sr, required_skills: [] }), true);
expect('request: multi-day ok', validate(ServiceRequestSchema, { ...sr, schedule_end: dt(30, 17) }), true);
expect('request: bad care type', validate(ServiceRequestSchema, { ...sr, care_type: 'petcare' }), false, 'valid care type', 'care_type');
expect('request: short description', validate(ServiceRequestSchema, { ...sr, description: 'help' }), false, 'at least 10', 'description');
expect('request: description over 2000', validate(ServiceRequestSchema, { ...sr, description: 'x'.repeat(2001) }), false, 'under 2000', 'description');
expect('request: null location', validate(ServiceRequestSchema, { ...sr, location_id: null }), false, 'select a location', 'location_id');
expect('request: empty location', validate(ServiceRequestSchema, { ...sr, location_id: '' }), false, 'select a location', 'location_id');
expect('request: bad urgency', validate(ServiceRequestSchema, { ...sr, urgency_level: 'apocalyptic' }), false, 'urgency', 'urgency_level');
expect('request: empty start', validate(ServiceRequestSchema, { ...sr, schedule_start: '' }), false, 'Start is required', 'schedule_start');
expect('request: garbage start', validate(ServiceRequestSchema, { ...sr, schedule_start: 'tomorrow-ish' }), false, 'valid date', 'schedule_start');
expect('request: end before start', validate(ServiceRequestSchema, { ...sr, schedule_end: dt(1) }), false, 'after the start', 'schedule_end');
expect('request: end equals start', validate(ServiceRequestSchema, { ...sr, schedule_end: sr.schedule_start }), false, 'after the start', 'schedule_end');
expect('request: under 1 hour', validate(ServiceRequestSchema, { ...sr, schedule_end: dt(2, 9, 30) }), false, 'at least 1 hour', 'schedule_end');
expect('request: over 180 days', validate(ServiceRequestSchema, { ...sr, schedule_end: dt(200, 17) }), false, '180 days', 'schedule_end');
expect('request: start in the past', validate(ServiceRequestSchema, { ...sr, schedule_start: dt(-3), schedule_end: dt(2, 17) }), false, 'in the past', 'schedule_start');
expect('request: start over a year ahead', validate(ServiceRequestSchema, { ...sr, schedule_start: dt(400), schedule_end: dt(400, 17) }), false, 'a year ahead', 'schedule_start');
// Cross-field schedule errors must surface even when other fields are also invalid.
const combined = validate(ServiceRequestSchema, { ...sr, description: 'x', location_id: null, schedule_start: dt(-3), schedule_end: dt(-4) });
expect('request: field + schedule errors together', { ok: ['description', 'location_id', 'schedule_start', 'schedule_end'].every((k) => k in (combined.fieldErrors || {})) }, true);

// ---------------- Booking ----------------
// No date fields here: the API reuses the service request's schedule.
const bk = { caregiver: 7, service_request: 3, notes: 'Gate code 4412' };
expect('booking: valid', validate(BookingSchema, bk), true);
expect('booking: empty notes ok', validate(BookingSchema, { ...bk, notes: '' }), true);
expect('booking: notes over 1000', validate(BookingSchema, { ...bk, notes: 'x'.repeat(1001) }), false, 'under 1000', 'notes');
expect('booking: caregiver missing', validate(BookingSchema, { ...bk, caregiver: 0 }), false, 'Caregiver is missing', 'caregiver');
expect('booking: request missing', validate(BookingSchema, { ...bk, service_request: -1 }), false, 'Service request is missing', 'service_request');

// ---------------- Review ----------------
expect('review: valid', validate(ReviewSchema, { booking: 1, rating: 5, comment: 'Great!' }), true);
expect('review: rating 1 boundary ok', validate(ReviewSchema, { booking: 1, rating: 1, comment: '' }), true);
expect('review: empty comment ok', validate(ReviewSchema, { booking: 1, rating: 3, comment: '' }), true);
expect('review: rating 0', validate(ReviewSchema, { booking: 1, rating: 0, comment: '' }), false, 'between 1 and 5', 'rating');
expect('review: rating 6', validate(ReviewSchema, { booking: 1, rating: 6, comment: '' }), false, 'between 1 and 5', 'rating');
expect('review: rating 4.5', validate(ReviewSchema, { booking: 1, rating: 4.5, comment: '' }), false, 'whole number', 'rating');
expect('review: rating NaN', validate(ReviewSchema, { booking: 1, rating: NaN, comment: '' }), false, 'number', 'rating');
expect('review: comment over 1000', validate(ReviewSchema, { booking: 1, rating: 5, comment: 'x'.repeat(1001) }), false, 'under 1000', 'comment');

// ---------------- validate() shape ----------------
const multi = validate(RegisterSchema, { first_name: '', last_name: '', email: 'bad', phone_number: 'nope', role: '', password: 'x', password_confirm: '' });
expect('shape: reports every failing field', { ok: ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password', 'password_confirm'].every((k) => k in multi.fieldErrors) }, true);
expect('shape: success returns cleaned data', (() => { const r = validate(ReviewSchema, { booking: 1, rating: 5, comment: '  neat  ' }); return { ok: r.ok && r.data.comment === 'neat' }; })(), true);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
