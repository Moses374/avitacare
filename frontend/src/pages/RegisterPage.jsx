import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { register, saveTokens, isLoggedIn } from '../api/auth'

const FIELDS = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password', 'password_confirm']

export default function RegisterPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone_number: '',
    role: 'family', password: '', password_confirm: '',
  })
  const [fieldErrors, setFieldErrors] = useState({})
  const [banner, setBanner] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw] = useState(false)
  const [showPwC, setShowPwC] = useState(false)

  useEffect(() => {
    if (isLoggedIn()) navigate('/dashboard', { replace: true })
    const role = params.get('role')
    if (role === 'family' || role === 'caregiver') {
      setForm(f => ({ ...f, role }))
    }
  }, [])

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
    setFieldErrors(fe => ({ ...fe, [e.target.name]: '' }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setFieldErrors({})
    setBanner('')
    setLoading(true)
    try {
      const data = await register(form)
      saveTokens(data.tokens.access, data.tokens.refresh)
      if (data.user?.first_name) localStorage.setItem('user_first_name', data.user.first_name)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      if (err.data && typeof err.data === 'object') {
        const errs = {}
        for (const [k, v] of Object.entries(err.data)) {
          errs[k] = Array.isArray(v) ? v[0] : v
        }
        setFieldErrors(errs)
      } else {
        setBanner(err.message || 'Registration failed.')
      }
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
      <div className="flex-1 flex items-start justify-center px-8 py-12 bg-bg overflow-y-auto">
        <div className="w-full max-w-md">
          <h1 className="text-2xl font-semibold text-text mb-1">Create your account</h1>
          <p className="text-sm text-muted mb-8">Join AvitaCare today</p>

          <form onSubmit={handleSubmit} noValidate>
            <div className="grid grid-cols-2 gap-4 mb-5">
              <div>
                <label className="form-label" htmlFor="first_name">First Name</label>
                <input className="form-input" type="text" id="first_name" name="first_name"
                  autoComplete="given-name" value={form.first_name} onChange={handleChange} required />
                {fieldErrors.first_name && <span className="form-error">{fieldErrors.first_name}</span>}
              </div>
              <div>
                <label className="form-label" htmlFor="last_name">Last Name</label>
                <input className="form-input" type="text" id="last_name" name="last_name"
                  autoComplete="family-name" value={form.last_name} onChange={handleChange} required />
                {fieldErrors.last_name && <span className="form-error">{fieldErrors.last_name}</span>}
              </div>
            </div>

            <div className="mb-5">
              <label className="form-label" htmlFor="email">Email</label>
              <input className="form-input" type="email" id="email" name="email"
                autoComplete="email" value={form.email} onChange={handleChange} required />
              {fieldErrors.email && <span className="form-error">{fieldErrors.email}</span>}
            </div>

            <div className="mb-5">
              <label className="form-label" htmlFor="phone_number">Phone Number</label>
              <input className="form-input" type="tel" id="phone_number" name="phone_number"
                autoComplete="tel" value={form.phone_number} onChange={handleChange} />
              {fieldErrors.phone_number && <span className="form-error">{fieldErrors.phone_number}</span>}
            </div>

            <div className="mb-5">
              <label className="form-label" htmlFor="role">I am</label>
              <select className="form-input" id="role" name="role" value={form.role} onChange={handleChange} required>
                <option value="family">I am looking for a Caregiver</option>
                <option value="caregiver">I am a Caregiver</option>
              </select>
              {fieldErrors.role && <span className="form-error">{fieldErrors.role}</span>}
            </div>

            <div className="mb-5">
              <label className="form-label" htmlFor="password">Password</label>
              <div className="relative">
                <input className="form-input pr-16" type={showPw ? 'text' : 'password'}
                  id="password" name="password" autoComplete="new-password"
                  value={form.password} onChange={handleChange} required />
                <button type="button" onClick={() => setShowPw(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted hover:text-text">
                  {showPw ? 'Hide' : 'Show'}
                </button>
              </div>
              {fieldErrors.password && <span className="form-error">{fieldErrors.password}</span>}
            </div>

            <div className="mb-6">
              <label className="form-label" htmlFor="password_confirm">Confirm Password</label>
              <div className="relative">
                <input className="form-input pr-16" type={showPwC ? 'text' : 'password'}
                  id="password_confirm" name="password_confirm" autoComplete="new-password"
                  value={form.password_confirm} onChange={handleChange} required />
                <button type="button" onClick={() => setShowPwC(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted hover:text-text">
                  {showPwC ? 'Hide' : 'Show'}
                </button>
              </div>
              {fieldErrors.password_confirm && <span className="form-error">{fieldErrors.password_confirm}</span>}
            </div>

            {banner && (
              <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 px-4 py-3">
                {banner}
              </div>
            )}

            <button type="submit" className="btn-primary w-full py-3" disabled={loading}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="text-sm text-muted mt-6 text-center">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
