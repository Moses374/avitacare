# AvitaCare — Demo Seed Data

Everything needed to load a full demo dataset into a fresh local environment.
Safe to run repeatedly — existing records are skipped, never duplicated.

## How to run

```bash
docker compose up -d
docker compose exec web python manage.py seed_demo
```

That one command seeds, in order:

| Step | What | Source |
|---|---|---|
| 1 | 348 Kenyan locations (counties + sub-counties), indexed into Meilisearch | `locations/management/commands/import_locations.py` |
| 2 | 14 users: 1 admin, 5 families, 8 caregivers | `accounts/management/commands/seed_users.py` |
| 3 | 6 service requests (all care types, mixed urgency) | `accounts/management/commands/seed_demo.py` |
| 4 | 4 bookings (2 completed, 1 confirmed, 1 pending) | 〃 |
| 5 | 2 reviews on completed bookings (populates caregiver ratings) | 〃 |
| 6 | 12 notifications (mixed read/unread, all categories) | 〃 |
| 7 | 6 admin audit-log entries | 〃 |

## Test accounts

All accounts use the password pattern shown per role.

### Admin — password `Admin1234!`

| Email | Notes |
|---|---|
| admin@avitacare.com | Superuser; also works for `/admin/` Django admin |

### Families — password `Family1234!`

| Email | Name | Location | Demo state |
|---|---|---|---|
| grace.mwangi@example.com | Grace Mwangi | Westlands | 2 completed bookings, 2 reviews left |
| daniel.omondi@example.com | Daniel Omondi | Kisumu | 1 confirmed upcoming booking |
| fatuma.hassan@example.com | Fatuma Hassan | Mombasa | 1 pending booking (high urgency) |
| peter.kamau@example.com | Peter Kamau | Nakuru | Open request, no booking yet |
| wanjiru.njoroge@example.com | Wanjiru Njoroge | Kiambu | Open urgent palliative request |

### Caregivers — password `Caregiver1234!`

| Email | Name | Location | Verification | Demo state |
|---|---|---|---|---|
| amina.wanjiru@example.com | Amina Wanjiru | Nairobi | verified | Completed booking, 5★ review |
| brian.otieno@example.com | Brian Otieno | Kisumu | verified | Confirmed upcoming booking |
| cynthia.achieng@example.com | Cynthia Achieng | Mombasa | verified | Pending booking to confirm |
| samuel.mutua@example.com | Samuel Mutua | Machakos | verified | No bookings yet |
| lydia.chebet@example.com | Lydia Chebet | Eldoret | verified | Completed booking, 4★ review |
| james.kariuki@example.com | James Kariuki | Nakuru | pending | Awaiting admin verification |
| mary.wangari@example.com | Mary Wangari | Kiambu | pending | Awaiting admin verification |
| kevin.odhiambo@example.com | Kevin Odhiambo | Nairobi | rejected | Rejected (incomplete documents) |

## Useful demo flows this data supports

- **Family flow**: log in as Grace → see completed bookings and reviews; as Peter/Wanjiru → open requests → "View matches" → book a verified caregiver.
- **Caregiver flow**: log in as Cynthia → pending booking to accept; as Amina → see rating/reviews.
- **Admin flow**: log in as admin → 2 pending verifications (James, Mary), populated audit log, user list, reports.

## Resetting

To wipe and reseed from scratch:

```bash
docker compose down
docker volume rm avitacare_avitacare-db-data avitacare_avitacare-search-data
docker compose up -d          # migrations run on startup
docker compose exec web python manage.py seed_demo
```

> These credentials are for local development only. Never load this seed into a production database.
