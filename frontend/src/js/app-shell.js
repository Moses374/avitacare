// Shared helpers for authenticated pages: auth/role guards, top-nav, sign out.
import { getProfile, logout, clearTokens } from '../api/auth.js';

export function requireAuth() {
  if (!localStorage.getItem('access_token')) {
    window.location.replace('login.html');
    return false;
  }
  return true;
}

export function setNavUser(name) {
  const el = document.getElementById('nav-username');
  if (el) el.textContent = name || '';
}

export function initSignOut(buttonId = 'signout-btn') {
  const btn = document.getElementById(buttonId);
  if (!btn) return;
  btn.addEventListener('click', async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      await logout(refresh);
    } catch {
      // Proceed with local cleanup regardless of the API result.
    }
    clearTokens();
    window.location.replace('login.html');
  });
}

function fullName(user) {
  return user.full_name || `${user.first_name} ${user.last_name}`.trim();
}

// Guard + bootstrap a page that only family users may view.
// Returns the user object, or null if the visitor was redirected away.
export async function initFamilyPage() {
  if (!requireAuth()) return null;

  const storedRole = localStorage.getItem('user_role');
  if (storedRole && storedRole !== 'family') {
    window.location.replace('dashboard.html');
    return null;
  }

  initSignOut();

  let user;
  try {
    user = await getProfile();
  } catch {
    clearTokens();
    window.location.replace('login.html');
    return null;
  }

  if (user.role !== 'family') {
    window.location.replace('dashboard.html');
    return null;
  }

  localStorage.setItem('user_role', user.role);
  setNavUser(fullName(user));
  return user;
}
