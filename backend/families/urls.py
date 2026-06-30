from django.urls import path

from .views import FamilyProfileView

urlpatterns = [
    path('profile/', FamilyProfileView.as_view(), name='family-profile'),
]
