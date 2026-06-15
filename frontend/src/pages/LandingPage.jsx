import React from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface">
      <Navbar />

      {/* Hero */}
      <section className="bg-gradient-to-br from-primary to-primary-dark text-white py-20 px-8">
        <div className="max-w-6xl mx-auto flex items-center gap-16">
          <div className="flex-1">
            <p className="text-xs font-medium tracking-widest uppercase text-white/70 mb-5">
              Caregiving, reimagined
            </p>
            <h1 className="text-4xl font-semibold leading-tight tracking-tight mb-5">
              Trusted caregivers for your family, when you need them most.
            </h1>
            <p className="text-base leading-relaxed text-white/85 max-w-lg mb-9">
              AvitaCare helps Kenyan families find verified, qualified caregivers for elderly care,
              childcare, post-surgical recovery, and disability support — all through one transparent platform.
            </p>
            <div className="flex gap-4 flex-wrap">
              <Link to="/register?role=family" className="btn-primary bg-white text-primary hover:bg-white/90 px-6 py-3">
                I need a caregiver
              </Link>
              <Link to="/register?role=caregiver" className="btn-ghost px-6 py-3">
                I am a caregiver
              </Link>
            </div>
          </div>
          <div className="flex-none w-96 flex justify-center items-center" aria-hidden="true">
            <svg width="400" height="350" viewBox="0 0 400 350" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="160" cy="195" r="60" stroke="white" strokeWidth="1.5" opacity="0.9"/>
              <circle cx="268" cy="212" r="38" stroke="white" strokeWidth="1.5" opacity="0.9"/>
              <line x1="100" y1="255" x2="306" y2="255" stroke="white" strokeWidth="1.5" opacity="0.45"/>
              <path d="M78 192 Q212 75 332 192" stroke="white" strokeWidth="1.5" strokeLinecap="round" fill="none" opacity="0.55"/>
              <circle cx="212" cy="106" r="4" fill="white" opacity="0.45"/>
              <line x1="78" y1="192" x2="78" y2="255" stroke="white" strokeWidth="1.5" opacity="0.35" strokeLinecap="round"/>
              <line x1="332" y1="192" x2="332" y2="255" stroke="white" strokeWidth="1.5" opacity="0.35" strokeLinecap="round"/>
            </svg>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-surface py-20 px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-semibold text-center tracking-tight mb-2">How AvitaCare works</h2>
          <p className="text-muted text-center mb-14">A simple, structured process from search to care delivery.</p>
          <div className="flex gap-12">
            {[
              { n: '01', title: 'Create your profile', desc: 'Register as a family or caregiver. Families describe their care needs. Caregivers list their qualifications, experience, and availability.' },
              { n: '02', title: 'Get matched', desc: 'Families submit a structured service request. Our system surfaces caregivers whose skills, location, and availability align with your needs.' },
              { n: '03', title: 'Book and manage', desc: 'Confirm your caregiver, manage the booking through the platform, and leave a review when the engagement is complete.' },
            ].map(({ n, title, desc }) => (
              <div key={n} className="flex-1">
                <div className="text-4xl font-semibold text-primary bg-primary-light inline-block px-2 py-0.5 mb-4 leading-tight">{n}</div>
                <div className="text-base font-semibold text-text mb-2">{title}</div>
                <p className="text-sm text-muted leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <hr className="max-w-6xl mx-auto border-border" />

      {/* Features */}
      <section className="bg-bg py-20 px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-semibold text-center tracking-tight mb-14">
            Why families and caregivers choose AvitaCare
          </h2>
          <div className="grid grid-cols-2 gap-x-16 gap-y-12">
            {[
              { title: 'Verified caregivers', desc: 'Every caregiver profile is reviewed by our administration team before going live. Families can see verified qualification summaries directly on each profile.' },
              { title: 'Structured matching', desc: 'Service requests are matched against caregiver profiles based on care type, location, and availability — not informal referrals or word of mouth.' },
              { title: 'Full booking lifecycle', desc: 'From request to completion, every engagement is tracked on the platform. Both parties have a clear record of what was agreed and when.' },
              { title: 'Transparent reviews', desc: 'After each completed booking, families leave a rating and written review. Caregivers build a public reputation that reflects their actual performance.' },
            ].map(({ title, desc }) => (
              <div key={title}>
                <div className="text-base font-semibold text-text mb-2">{title}</div>
                <p className="text-sm text-muted leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary text-white py-20 px-8 text-center">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-semibold tracking-tight mb-3">Ready to get started?</h2>
          <p className="text-base text-white/85 mb-9">
            Join families and caregivers across Kenya who are already using AvitaCare.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/register?role=family" className="btn-primary bg-white text-primary hover:bg-white/90 px-6 py-3">
              Register as a Family
            </Link>
            <Link to="/register?role=caregiver" className="btn-ghost px-6 py-3">
              Register as a Caregiver
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface border-t border-border py-6 px-8">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span className="text-sm text-muted">AvitaCare</span>
          <span className="text-sm text-muted">Built for Kenya. &copy; 2026 AvitaCare.</span>
        </div>
      </footer>
    </div>
  )
}
