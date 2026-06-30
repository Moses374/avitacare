"""
Management command: seed_users

Creates a realistic set of demo users:
  - 1 admin
  - 5 family accounts (with household profiles)
  - 8 caregiver accounts (mix of verified, pending, rejected)

Safe to re-run: skips any email that already exists.
"""

from django.core.management.base import BaseCommand

from accounts.models import User, get_or_create_subclass
from caregivers.models import CaregiverProfile
from families.models import FamilyProfile
from locations.models import Location


def loc(name):
    """Return a Location by display_name fragment, or None."""
    qs = Location.objects.filter(display_name__icontains=name)
    return qs.first()


ADMIN = {
    'email': 'admin@avitacare.com',
    'password': 'Admin1234!',
    'first_name': 'Admin',
    'last_name': 'Avitacare',
    'role': 'admin',
    'is_staff': True,
    'is_superuser': True,
}

FAMILIES = [
    {
        'email': 'grace.mwangi@example.com',
        'password': 'Family1234!',
        'first_name': 'Grace',
        'last_name': 'Mwangi',
        'phone_number': '+254701000001',
        'location': 'Westlands',
        'preferred_caregiver_type': 'elderly',
        'care_recipient_name': 'Margaret Mwangi',
        'care_recipient_details': '74-year-old with mild arthritis. Needs daily mobility assistance and medication reminders.',
    },
    {
        'email': 'daniel.omondi@example.com',
        'password': 'Family1234!',
        'first_name': 'Daniel',
        'last_name': 'Omondi',
        'phone_number': '+254701000002',
        'location': 'Kisumu',
        'preferred_caregiver_type': 'child',
        'care_recipient_name': 'Liam Omondi',
        'care_recipient_details': '5-year-old with speech delay. Attends therapy twice a week and benefits from structured play.',
    },
    {
        'email': 'fatuma.hassan@example.com',
        'password': 'Family1234!',
        'first_name': 'Fatuma',
        'last_name': 'Hassan',
        'phone_number': '+254701000003',
        'location': 'Mombasa',
        'preferred_caregiver_type': 'post_hospital',
        'care_recipient_name': 'Ibrahim Hassan',
        'care_recipient_details': '58-year-old recovering from hip replacement surgery. Needs physio support and help with daily tasks.',
    },
    {
        'email': 'peter.kamau@example.com',
        'password': 'Family1234!',
        'first_name': 'Peter',
        'last_name': 'Kamau',
        'phone_number': '+254701000004',
        'location': 'Nakuru',
        'preferred_caregiver_type': 'disability',
        'care_recipient_name': 'Sarah Kamau',
        'care_recipient_details': '32-year-old with cerebral palsy. Requires full-time personal assistance including mobility and feeding.',
    },
    {
        'email': 'wanjiru.njoroge@example.com',
        'password': 'Family1234!',
        'first_name': 'Wanjiru',
        'last_name': 'Njoroge',
        'phone_number': '+254701000005',
        'location': 'Kiambu',
        'preferred_caregiver_type': 'palliative',
        'care_recipient_name': 'Joseph Njoroge',
        'care_recipient_details': 'Palliative care for a 68-year-old with terminal illness. Comfort-focused, pain management support required.',
    },
]

CAREGIVERS = [
    {
        'email': 'amina.wanjiru@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Amina',
        'last_name': 'Wanjiru',
        'phone_number': '+254702000001',
        'location': 'Nairobi',
        'bio': 'Dedicated elderly care specialist with 9 years of experience supporting seniors with mobility challenges and memory conditions.',
        'skills': ['elderly_care', 'palliative_care'],
        'certifications': ['Certificate in Geriatric Care', 'First Aid Level 2'],
        'years_experience': 9,
        'verification_status': 'verified',
    },
    {
        'email': 'brian.otieno@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Brian',
        'last_name': 'Otieno',
        'phone_number': '+254702000002',
        'location': 'Kisumu',
        'bio': 'Child development professional specialising in support for children with autism spectrum disorder and learning difficulties.',
        'skills': ['child_care', 'disability_support'],
        'certifications': ['Diploma in Early Childhood Development', 'ASD Awareness Certificate'],
        'years_experience': 6,
        'verification_status': 'verified',
    },
    {
        'email': 'cynthia.achieng@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Cynthia',
        'last_name': 'Achieng',
        'phone_number': '+254702000003',
        'location': 'Mombasa',
        'bio': 'Post-surgical and rehabilitation caregiver. Works closely with physiotherapists to support patient recovery at home.',
        'skills': ['post_hospital_recovery', 'elderly_care'],
        'certifications': ['Certificate in Home-Based Care', 'Physiotherapy Assistant Training'],
        'years_experience': 4,
        'verification_status': 'verified',
    },
    {
        'email': 'samuel.mutua@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Samuel',
        'last_name': 'Mutua',
        'phone_number': '+254702000004',
        'location': 'Machakos',
        'bio': 'Experienced disability support worker with a background in occupational therapy assistance and personal care.',
        'skills': ['disability_support', 'post_hospital_recovery'],
        'certifications': ['Diploma in Disability Studies', 'First Aid Certified'],
        'years_experience': 7,
        'verification_status': 'verified',
    },
    {
        'email': 'lydia.chebet@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Lydia',
        'last_name': 'Chebet',
        'phone_number': '+254702000005',
        'location': 'Eldoret',
        'bio': 'Palliative care nurse aide with compassionate approach to end-of-life support for patients and their families.',
        'skills': ['palliative_care', 'elderly_care'],
        'certifications': ['Certificate in Palliative Care', 'Nursing Aide Certification'],
        'years_experience': 5,
        'verification_status': 'verified',
    },
    {
        'email': 'james.kariuki@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'James',
        'last_name': 'Kariuki',
        'phone_number': '+254702000006',
        'location': 'Nakuru',
        'bio': 'Recent nursing graduate seeking to build experience in home-based care. Enthusiastic and quick to learn.',
        'skills': ['elderly_care', 'child_care'],
        'certifications': ['Diploma in Nursing'],
        'years_experience': 1,
        'verification_status': 'pending',
    },
    {
        'email': 'mary.wangari@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Mary',
        'last_name': 'Wangari',
        'phone_number': '+254702000007',
        'location': 'Kiambu',
        'bio': 'Home care professional with experience in both child and elderly care, currently seeking verification.',
        'skills': ['child_care', 'disability_support'],
        'certifications': ['Certificate in Community Health'],
        'years_experience': 3,
        'verification_status': 'pending',
    },
    {
        'email': 'kevin.odhiambo@example.com',
        'password': 'Caregiver1234!',
        'first_name': 'Kevin',
        'last_name': 'Odhiambo',
        'phone_number': '+254702000008',
        'location': 'Nairobi',
        'bio': 'Application rejected due to incomplete documentation submitted during the verification process.',
        'skills': ['elderly_care'],
        'certifications': [],
        'years_experience': 2,
        'verification_status': 'rejected',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo users (admin, families, caregivers)'

    def handle(self, *args, **options):
        created_total = 0
        skipped_total = 0

        # Admin
        if not User.objects.filter(email=ADMIN['email']).exists():
            User.objects.create_superuser(
                email=ADMIN['email'],
                password=ADMIN['password'],
                first_name=ADMIN['first_name'],
                last_name=ADMIN['last_name'],
            )
            self.stdout.write(self.style.SUCCESS(f"  [admin]  Created {ADMIN['email']}"))
            created_total += 1
        else:
            self.stdout.write(f"  [admin]  Skipped {ADMIN['email']} (already exists)")
            skipped_total += 1

        # Families
        self.stdout.write('\nFamilies:')
        for data in FAMILIES:
            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  Skipped {data['email']}")
                skipped_total += 1
                continue

            user = User.objects.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data.get('phone_number', ''),
                role='family',
            )
            profile, _ = get_or_create_subclass(FamilyProfile, user)
            profile.location = loc(data['location'])
            profile.preferred_caregiver_type = data.get('preferred_caregiver_type', '')
            profile.care_recipient_name = data.get('care_recipient_name', '')
            profile.care_recipient_details = data.get('care_recipient_details', '')
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"  Created {data['email']}"))
            created_total += 1

        # Caregivers
        self.stdout.write('\nCaregivers:')
        for data in CAREGIVERS:
            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  Skipped {data['email']}")
                skipped_total += 1
                continue

            user = User.objects.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data.get('phone_number', ''),
                role='caregiver',
            )
            profile, _ = get_or_create_subclass(CaregiverProfile, user)
            profile.location = loc(data['location'])
            profile.bio = data.get('bio', '')
            profile.skills = data.get('skills', [])
            profile.certifications = data.get('certifications', [])
            profile.years_experience = data.get('years_experience', 0)
            profile.verification_status = data.get('verification_status', 'pending')
            profile.save()
            status_label = data['verification_status'].upper()
            self.stdout.write(self.style.SUCCESS(f"  Created {data['email']} [{status_label}]"))
            created_total += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nDone. {created_total} created, {skipped_total} skipped.')
        )
