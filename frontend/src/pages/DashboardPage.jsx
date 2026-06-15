import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { clearTokens, logout, getProfile } from '../api/auth'
import Navbar from '../components/Navbar'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const firstName = localStorage.getItem('user_first_name') || 'there'

  useEffect(() => {
    getProfile()
      .then(setUser)
      .catch(() => {})
  }, [])

  async function handleLogout() {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) await logout(refresh)
    } catch (_) {}
    clearTokens()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-bg">
      <Navbar />
      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-text">
            Welcome back, {user?.first_name || firstName}.
          </h1>
          <p className="text-sm text-muted mt-1">
            {user?.role === 'caregiver'
              ? 'Manage your caregiver profile and bookings.'
              : 'Find and manage caregivers for your family.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-surface border border-border p-6">
            <div className="text-xs font-medium uppercase tracking-wide text-muted mb-1">Role</div>
            <div className="text-lg font-semibold text-text capitalize">{user?.role || '—'}</div>
          </div>
          <div className="bg-surface border border-border p-6">
            <div className="text-xs font-medium uppercase tracking-wide text-muted mb-1">Email</div>
            <div className="text-sm text-text truncate">{user?.email || '—'}</div>
          </div>
          <div className="bg-surface border border-border p-6">
            <div className="text-xs font-medium uppercase tracking-wide text-muted mb-1">Phone</div>
            <div className="text-sm text-text">{user?.phone_number || '—'}</div>
          </div>
        </div>

        <div className="mt-12 bg-surface border border-border p-8 text-center">
          <p className="text-muted text-sm">
            Dashboard features (bookings, matching, profiles) coming soon.
          </p>
        </div>
      </div>
    </div>
  )
}
