import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { isLoggedIn, clearTokens, logout } from '../api/auth'

export default function Navbar() {
  const navigate = useNavigate()
  const loggedIn = isLoggedIn()

  async function handleLogout() {
    try {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) await logout(refresh)
    } catch (_) {}
    clearTokens()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-50 bg-surface border-b border-border">
      <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold text-primary no-underline">
          AvitaCare
        </Link>
        <div className="flex items-center gap-6">
          {loggedIn ? (
            <>
              <Link to="/dashboard" className="text-sm font-medium text-text hover:text-primary transition-colors">
                Dashboard
              </Link>
              <button
                onClick={handleLogout}
                className="text-sm font-medium text-text hover:text-primary transition-colors"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium text-text hover:text-primary transition-colors">
                Sign in
              </Link>
              <Link to="/register" className="btn-primary text-sm px-5 py-2">
                Get started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
