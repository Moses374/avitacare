import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login, saveTokens, isLoggedIn } from '../api/auth'

export default function LoginPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isLoggedIn()) {
    navigate('/dashboard', { replace: true })
    return null
  }

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(form.email, form.password)
      saveTokens(data.access, data.refresh)
      if (data.user?.first_name) {
        localStorage.setItem('user_first_name', data.user.first_name)
      }
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Brand panel */}
      <div className="hidden lg:flex flex-col justify-center px-16 bg-primary text-white w-[480px] flex-none">
        <div className="text-2xl font-semibold mb-3">AvitaCare</div>
        <div className="text-base text-white/80 leading-relaxed">
          Connecting families with trusted caregivers across Kenya
        </div>
        <div className="mt-12" aria-hidden="true">
          <svg width="160" height="120" viewBox="0 0 160 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M30 90 C28 85 26 78 27 70 C28 62 32 58 36 58 C38 58 40 59 41 61 L41 40 C41 36 44 33 47 33 C50 33 53 36 53 40 L53 55 C54 53 56 52 59 52 C62 52 65 55 65 58 L65 62 C66 60 68 59 71 59 C74 59 77 62 77 65 L77 75 C78 74 80 73 82 73 C85 73 88 76 88 79 L88 90 C88 100 80 108 70 108 L50 108 C40 108 32 100 30 90 Z"
              stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex-1 flex items-center justify-center px-8 py-16 bg-bg">
        <div className="w-full max-w-md">
          <h1 className="text-2xl font-semibold text-text mb-1">Welcome back</h1>
          <p className="text-sm text-muted mb-8">Sign in to your AvitaCare account</p>

          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-5">
              <label className="form-label" htmlFor="email">Email</label>
              <input
                className="form-input"
                type="email"
                id="email"
                name="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="mb-6">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                className="form-input"
                type="password"
                id="password"
                name="password"
                autoComplete="current-password"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>

            {error && (
              <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 px-4 py-3">
                {error}
              </div>
            )}

            <button type="submit" className="btn-primary w-full py-3" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="text-sm text-muted mt-6 text-center">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="text-primary font-medium hover:underline">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
