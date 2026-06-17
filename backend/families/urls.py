from django.urls import path

from .views import (
    FamilyProfileView,
    ServiceRequestListCreateView,
    ServiceRequestDetailView,
)

urlpatterns = [
    path('profile/', FamilyProfileView.as_view(), name='family-profile'),
    path('requests/', ServiceRequestListCreateView.as_view(), name='service-request-list'),
    path('requests/<int:pk>/', ServiceRequestDetailView.as_view(), name='service-request-detail'),
]
