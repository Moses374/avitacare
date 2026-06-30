from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

FRONTEND_PAGES = ['index.html', 'login.html', 'register.html']
FRONTEND_PAGES += [f'family/{p}.html' for p in (
    'dashboard', 'profile', 'requests', 'caregivers', 'bookings', 'reviews', 'notifications', 'settings',
)]
FRONTEND_PAGES += [f'caregiver/{p}.html' for p in (
    'dashboard', 'profile', 'bookings', 'reviews', 'notifications', 'settings',
)]

frontend_urlpatterns = [
    path(
        '' if page == 'index.html' else page,
        TemplateView.as_view(template_name=page),
        name=f'page-{page.replace("/", "-").replace(".html", "")}',
    )
    for page in FRONTEND_PAGES
]

# Admin section served at /admin/<page> (clean URLs, no .html)
ADMIN_PAGES = ['verifications', 'users', 'audit-log', 'reports', 'notifications', 'settings']

admin_urlpatterns = [
    path('admin/', TemplateView.as_view(template_name='admin/dashboard.html'), name='page-admin'),
    *[
        path(f'admin/{p}', TemplateView.as_view(template_name=f'admin/{p}.html'), name=f'page-admin-{p}')
        for p in ADMIN_PAGES
    ],
]

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),

    *frontend_urlpatterns,
    *admin_urlpatterns,

    path('api/auth/', include('accounts.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/caregivers/', include('caregivers.urls')),
    path('api/families/', include('families.urls')),
    path('api/requests/', include('service_requests.urls')),
    path('api/matching/', include('matching.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/admin-portal/', include('admin_portal.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
