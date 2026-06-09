from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App routes
    path('api/users/', include('users.urls')),
    path('api/caregivers/', include('caregivers.urls')),
    path('api/families/', include('families.urls')),
    path('api/requests/', include('service_requests.urls')),
    path('api/matching/', include('matching.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/admin-portal/', include('admin_portal.urls')),
]
