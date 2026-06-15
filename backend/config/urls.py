from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/caregivers/', include('caregivers.urls')),
    path('api/families/', include('families.urls')),
]
