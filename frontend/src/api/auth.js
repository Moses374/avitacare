const BASE = '/api/auth'

async function request(url, options = {}) {
  const res = await fetch(url, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.detail || data.message || 'Request failed')
    err.data = data
    throw err
  }
  return data
}

export function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_first_name')
}

export function isLoggedIn() {
  return !!localStorage.getItem('access_token')
}

export function getAccessToken() {
  return localStorage.getItem('access_token')
}

export function register(data) {
  return request(`${BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function login(email, password) {
  return request(`${BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
}

export function logout(refreshToken) {
  return request(`${BASE}/logout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getAccessToken()}`,
    },
    body: JSON.stringify({ refresh: refreshToken }),
  })
}

export function refreshAccessToken(refresh) {
  return request(`${BASE}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
}

export function getProfile() {
  return request(`${BASE}/profile/`, {
    headers: { Authorization: `Bearer ${getAccessToken()}` },
  })
}
