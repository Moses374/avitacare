from django.urls import path

from .views import (
    CaregiverAvailabilityView,
    CaregiverDetailView,
    CaregiverDocumentUploadView,
    CaregiverListView,
    CaregiverProfileView,
)

urlpatterns = [
    path('profile/', CaregiverProfileView.as_view(), name='caregiver-profile'),
    path('availability/', CaregiverAvailabilityView.as_view(), name='caregiver-availability'),
    path('documents/', CaregiverDocumentUploadView.as_view(), name='caregiver-documents'),
    path('', CaregiverListView.as_view(), name='caregiver-list'),
    path('<int:pk>/', CaregiverDetailView.as_view(), name='caregiver-detail'),
]
