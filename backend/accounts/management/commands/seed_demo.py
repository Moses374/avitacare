"""
Management command: seed_demo

One-shot demo dataset for local development. Layers, in order:
  1. Locations   — Kenya counties/sub-counties (import_locations) + Meilisearch index
  2. Users       — admin, 5 families, 8 caregivers (seed_users; see that file for credentials)
  3. Service requests — one per family, mixed care types/urgency
  4. Bookings    — completed / confirmed / pending against those requests
  5. Reviews     — on completed bookings (also populates caregiver avg ratings)
  6. Notifications — a realistic mix of read/unread per role
  7. Audit log   — admin verification actions

Safe to re-run: every step is idempotent (get_or_create keyed on natural fields).

Usage:
  docker compose exec web python manage.py seed_demo
"""

from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from admin_portal.models import AuditLog
from bookings.models import Booking
from locations.models import Location
from notifications.models import Notification
from reviews.models import Review
from service_requests.models import ServiceRequest


def loc(name):
    return Location.objects.filter(display_name__icontains=name).first()


def user(email):
    return User.objects.get(email=email)


# ---- Service requests ----------------------------------------------------
# `description` doubles as the idempotency key, so keep each one unique.
# `booking` links the request to a caregiver + booking status; None = still open.

SERVICE_REQUESTS = [
    {
        'family': 'grace.mwangi@example.com',
        'care_type': 'elderly',
        'description': 'Daily support for my 74-year-old mother: mobility assistance, medication reminders and companionship on weekday mornings.',
        'location': 'Westlands',
        'urgency_level': 'medium',
        'required_skills': ['elderly_care'],
        'start_days': -10, 'end_days': -10, 'duration_hours': 8,
        'status': 'matched',
        'booking': {
            'caregiver': 'amina.wanjiru@example.com',
            'status': 'completed',
            'notes': 'Gate code is 4412. Mum prefers her walk before 10am.',
            'review': {'rating': 5, 'comment': 'Amina was wonderful — patient, punctual and genuinely caring. My mother looks forward to her visits.'},
        },
    },
    {
        'family': 'grace.mwangi@example.com',
        'care_type': 'palliative',
        'description': 'Weekend relief care for my mother while our regular caregiver is away. Comfort-focused support and meal preparation.',
        'location': 'Westlands',
        'urgency_level': 'low',
        'required_skills': ['palliative_care', 'elderly_care'],
        'start_days': -21, 'end_days': -19, 'duration_hours': 0,
        'status': 'matched',
        'booking': {
            'caregiver': 'lydia.chebet@example.com',
            'status': 'completed',
            'notes': 'Weekend cover only, Saturday and Sunday.',
            'review': {'rating': 4, 'comment': 'Lydia was kind and professional. Slightly late on Sunday but communicated well in advance.'},
        },
    },
    {
        'family': 'daniel.omondi@example.com',
        'care_type': 'child',
        'description': 'After-school care for our 5-year-old son with speech delay: structured play, homework help and drop-off at Tuesday therapy sessions.',
        'location': 'Kisumu',
        'urgency_level': 'medium',
        'required_skills': ['child_care'],
        'start_days': 2, 'end_days': 2, 'duration_hours': 5,
        'status': 'matched',
        'booking': {
            'caregiver': 'brian.otieno@example.com',
            'status': 'confirmed',
            'notes': 'Pick-up from Aga Khan Primary at 3:30pm. Liam responds well to routine.',
        },
    },
    {
        'family': 'fatuma.hassan@example.com',
        'care_type': 'post_hospital',
        'description': 'Post-surgery recovery support for my husband after hip replacement: physio exercises, wound-care reminders and help with daily tasks.',
        'location': 'Mombasa',
        'urgency_level': 'high',
        'required_skills': ['post_hospital_recovery'],
        'start_days': 1, 'end_days': 15, 'duration_hours': 0,
        'status': 'matched',
        'booking': {
            'caregiver': 'cynthia.achieng@example.com',
            'status': 'pending',
            'notes': 'Physio plan from Coast General available on arrival.',
        },
    },
    {
        'family': 'peter.kamau@example.com',
        'care_type': 'disability',
        'description': 'Full-time weekday personal assistant for my 32-year-old sister with cerebral palsy: mobility, feeding and communication support.',
        'location': 'Nakuru',
        'urgency_level': 'medium',
        'required_skills': ['disability_support'],
        'start_days': 7, 'end_days': 37, 'duration_hours': 0,
        'status': 'open',
        'booking': None,
    },
    {
        'family': 'wanjiru.njoroge@example.com',
        'care_type': 'palliative',
        'description': 'Urgent palliative care for my 68-year-old father: pain management support, comfort care and overnight presence.',
        'location': 'Kiambu',
        'urgency_level': 'high',
        'required_skills': ['palliative_care'],
        'start_days': 1, 'end_days': 30, 'duration_hours': 0,
        'status': 'open',
        'booking': None,
    },
]

NOTIFICATIONS = [
    ('grace.mwangi@example.com', 'booking', 'Your booking with Amina Wanjiru is complete. Leave a review!', True),
    ('grace.mwangi@example.com', 'review', 'Thanks for reviewing Amina Wanjiru.', True),
    ('daniel.omondi@example.com', 'booking', 'Brian Otieno confirmed your booking starting this week.', False),
    ('fatuma.hassan@example.com', 'booking', 'Your booking request was sent to Cynthia Achieng.', False),
    ('amina.wanjiru@example.com', 'verification', 'Your caregiver profile has been verified. You can now receive bookings.', True),
    ('amina.wanjiru@example.com', 'review', 'Grace Mwangi left you a 5-star review.', False),
    ('brian.otieno@example.com', 'booking', 'New booking from Daniel Omondi — please confirm the schedule.', False),
    ('cynthia.achieng@example.com', 'booking', 'New booking request from Fatuma Hassan is awaiting your confirmation.', False),
    ('lydia.chebet@example.com', 'review', 'Grace Mwangi left you a 4-star review.', False),
    ('james.kariuki@example.com', 'verification', 'Your application is under review. We may request additional documents.', False),
    ('kevin.odhiambo@example.com', 'verification', 'Your verification was rejected: incomplete documentation. You may re-apply.', False),
    ('admin@avitacare.com', 'verification', '2 caregiver applications are awaiting verification.', False),
]

AUDIT_LOGS = [
    ('Verified caregiver', 'amina.wanjiru@example.com', 'Documents complete: geriatric care certificate and first aid verified.'),
    ('Verified caregiver', 'brian.otieno@example.com', 'ECD diploma and ASD certificate verified.'),
    ('Verified caregiver', 'cynthia.achieng@example.com', 'Home-based care certificate verified.'),
    ('Verified caregiver', 'samuel.mutua@example.com', 'Disability studies diploma verified.'),
    ('Verified caregiver', 'lydia.chebet@example.com', 'Palliative care certificate and nursing aide certification verified.'),
    ('Rejected caregiver verification', 'kevin.odhiambo@example.com', 'Submitted documents were incomplete: missing certification evidence.'),
]


class Command(BaseCommand):
    help = 'Seed the full demo dataset: locations, users, requests, bookings, reviews, notifications, audit log.'

    def handle(self, *args, **options):
        now = timezone.now()

        # 1. Locations
        self.stdout.write(self.style.MIGRATE_HEADING('1/7 Locations'))
        if Location.objects.exists():
            self.stdout.write(f'  Skipped import ({Location.objects.count()} already present).')
        else:
            call_command('import_locations')
        try:
            call_command('index_locations')
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f'  Meilisearch indexing skipped: {exc}'))

        # 2. Users
        self.stdout.write(self.style.MIGRATE_HEADING('2/7 Users'))
        call_command('seed_users')

        # 3–5. Service requests, bookings, reviews
        self.stdout.write(self.style.MIGRATE_HEADING('3/7 Service requests, 4/7 Bookings, 5/7 Reviews'))
        for spec in SERVICE_REQUESTS:
            family = user(spec['family'])
            start = (now + timedelta(days=spec['start_days'])).replace(hour=9, minute=0, second=0, microsecond=0)
            if spec['duration_hours']:
                end = start + timedelta(hours=spec['duration_hours'])
            else:
                end = (now + timedelta(days=spec['end_days'])).replace(hour=18, minute=0, second=0, microsecond=0)

            request, created = ServiceRequest.objects.get_or_create(
                family=family,
                description=spec['description'],
                defaults={
                    'care_type': spec['care_type'],
                    'location': loc(spec['location']),
                    'urgency_level': spec['urgency_level'],
                    'required_skills': spec['required_skills'],
                    'schedule_start': start,
                    'schedule_end': end,
                    'status': spec['status'],
                },
            )
            tag = 'Created' if created else 'Skipped'
            self.stdout.write(f"  [{tag}] {spec['care_type']} request — {family.full_name}")

            booking_spec = spec['booking']
            if not booking_spec:
                continue

            caregiver = user(booking_spec['caregiver'])
            booking, created = Booking.objects.get_or_create(
                service_request=request,
                defaults={
                    'caregiver': caregiver,
                    'family': family,
                    'status': booking_spec['status'],
                    'scheduled_start': request.schedule_start,
                    'scheduled_end': request.schedule_end,
                    'notes': booking_spec['notes'],
                },
            )
            tag = 'Created' if created else 'Skipped'
            self.stdout.write(f"    [{tag}] booking → {caregiver.full_name} [{booking_spec['status']}]")

            review_spec = booking_spec.get('review')
            if review_spec:
                _, created = Review.objects.get_or_create(
                    booking=booking,
                    defaults={'rating': review_spec['rating'], 'comment': review_spec['comment']},
                )
                tag = 'Created' if created else 'Skipped'
                self.stdout.write(f"      [{tag}] review {review_spec['rating']}/5")

        # 6. Notifications
        self.stdout.write(self.style.MIGRATE_HEADING('6/7 Notifications'))
        created_count = 0
        for email, category, message, is_read in NOTIFICATIONS:
            _, created = Notification.objects.get_or_create(
                recipient=user(email),
                message=message,
                defaults={'category': category, 'is_read': is_read},
            )
            created_count += created
        self.stdout.write(f'  {created_count} created, {len(NOTIFICATIONS) - created_count} skipped.')

        # 7. Audit log
        self.stdout.write(self.style.MIGRATE_HEADING('7/7 Audit log'))
        admin = user('admin@avitacare.com')
        created_count = 0
        for action, target_email, details in AUDIT_LOGS:
            _, created = AuditLog.objects.get_or_create(
                admin=admin,
                action=action,
                target_user=user(target_email),
                defaults={'details': details},
            )
            created_count += created
        self.stdout.write(f'  {created_count} created, {len(AUDIT_LOGS) - created_count} skipped.')

        self.stdout.write(self.style.SUCCESS('\nDemo dataset ready. Credentials are listed in SEED_DATA.md.'))
