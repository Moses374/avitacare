# Avitacare

A Web-Based Caregiver Coordination System for Matching Families with Verified Caregivers in Kenya.

> Strathmore University — ICS 3 Group F  
> Supervisor: Dr. Stephen Obonyo  
> Students: Moses Kibet Kipkemboi (183638) · Collins Jared Orina (184587)

---

## Overview

Avitacare is a centralised digital platform that connects families with verified, qualified caregivers across Kenya. It addresses the fragmented, informal caregiver sourcing market by introducing structured profiles, credential verification, criteria-based matching, booking lifecycle management, and a public ratings system.

---

## Architecture

The system follows a **three-tier client-server architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│          HTML · CSS · JavaScript (Responsive)           │
│   Caregiver UI │ Family UI │ Admin Dashboard            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────┐
│                APPLICATION LOGIC LAYER                  │
│            Python · Django REST Framework               │
│                                                         │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────┐  │
│  │ Auth / RBAC  │  │ Matching Engine│  │Priority    │  │
│  │ JWT Tokens   │  │ Graph-based    │  │Queue Mgr   │  │
│  └──────────────┘  └────────────────┘  └────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────┐  │
│  │ Booking      │  │ Caregiver      │  │ Admin      │  │
│  │ Lifecycle    │  │ Profile Mgmt   │  │ Portal     │  │
│  └──────────────┘  └────────────────┘  └────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ ORM (Django)
┌────────────────────────▼────────────────────────────────┐
│                     DATA LAYER                          │
│                    PostgreSQL                           │
│  Users │ CaregiverProfiles │ FamilyProfiles │ Bookings  │
│  ServiceRequests │ Reviews │ AuditLogs                  │
└─────────────────────────────────────────────────────────┘
```

### Actor Roles (RBAC)

| Role | Capabilities |
|------|-------------|
| **Caregiver** | Register profile, upload documents, set availability, respond to bookings |
| **Family** | Submit service requests, browse & match caregivers, confirm bookings, submit reviews |
| **Administrator** | Verify caregiver documents, manage users, oversee bookings, audit activity |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3, Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT (JSON Web Tokens) |
| Design Pattern | Object-Oriented (OOAD) |
| Development Model | Incremental Development |

---

## Project Structure

```
avitacare/
├── backend/
│   ├── avitacare/            # Django project config (settings, urls, wsgi)
│   ├── users/                # Base User model, JWT auth, RBAC
│   ├── caregivers/           # Caregiver profiles, document upload
│   ├── families/             # Family profiles, care recipient details
│   ├── service_requests/     # Structured service request forms
│   ├── matching/             # Graph-based matching + priority queue engine
│   ├── bookings/             # Booking lifecycle (pending→confirmed→completed)
│   ├── reviews/              # Ratings and written reviews
│   └── admin_portal/         # Admin verification, audit logs, user management
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── caregiver/
│       ├── family/
│       └── admin/
├── docs/
│   ├── wireframes/
│   ├── diagrams/             # UML: use case, sequence, class, ERD, activity
│   └── proposal.pdf
├── manage.py
├── requirements.txt
└── README.md
```

---

## Core Modules

### 1. Authentication Module
- Role-based registration (Caregiver / Family / Administrator)
- Password hashing and JWT token generation
- Middleware-level access control per role

### 2. Caregiver Profile Module
- Profile fields: qualifications, certifications, experience, specialisations, location, availability
- Document submission for admin verification
- Real-time availability updates to prevent double-bookings

### 3. Family & Service Request Module
- Structured service request form: care type, recipient details, location, schedule, urgency level
- Criteria-based matching against verified caregiver profiles
- Ranked shortlist returned to the family

### 4. Matching Engine
- **Graph-based matching** — models caregiver–request relationships, scores suitability by skills, location proximity, and availability
- **Priority Queue** — surfaces urgent requests (e.g. post-hospital discharge) to the top

### 5. Booking & Scheduling Module
- Full lifecycle tracking: `pending → confirmed → ongoing → completed`
- Automatic availability lock on confirmation
- Booking history for both parties

### 6. Administration Module
- Document review dashboard (approve / reject caregiver registrations)
- User account management and deactivation
- Immutable audit log of all admin actions

### 7. Ratings & Review Module
- Unlocked only on booking completion
- Numerical rating + optional written review
- Aggregated reputation score displayed on caregiver public profile

---

## Database Schema (Key Entities)

```
User (base)
├── Caregiver  (skills, certifications, experience, avg_rating, availability)
└── Family     (location, care_recipient_details, preferred_care_type)

ServiceRequest  (family_id, care_type, location, schedule, urgency, status)
Booking         (caregiver_id, family_id, service_request_id, dates, status)
Review          (booking_id, rating, comment, created_at)
AuditLog        (admin_id, action, target, timestamp)
```

Cardinality rules:
- A Caregiver → many Bookings; each Booking → exactly one Caregiver + one Family
- A Family → many ServiceRequests; each ServiceRequest → one Family
- A completed Booking → at most one Review

---

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/Moses374/avitacare.git
cd avitacare

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY, etc.

# Run migrations
python manage.py migrate

# Create superuser (Admin role)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Environment Variables

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/avitacare
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Deliverables Tracker

- [x] System Proposal
- [ ] Authentication Module
- [ ] Caregiver Profile Module
- [ ] Family & Service Request Module
- [ ] Booking & Scheduling Module
- [ ] Administration Module
- [ ] Ratings & Review Module

---

## Scope & Limitations

**In scope (v1.0):**
- Web browser access (desktop + mobile via responsive design)
- Criteria-based caregiver matching
- Admin-managed credential verification
- Full booking lifecycle management
- Ratings and reviews

**Out of scope (v1.0):**
- External healthcare system integrations
- SMS notifications
- Payment gateway
- Native mobile app

**Target geography:** Urban and peri-urban Kenya (Nairobi focus).

---

## License

Academic project — Strathmore University, 2026.
