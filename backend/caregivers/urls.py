from django.urls import path
from .views import CaregiverListView, CaregiverDetailView, MyCaregiverProfileView

urlpatterns = [
    path('', CaregiverListView.as_view(), name='caregiver-list'),
    path('<int:pk>/', CaregiverDetailView.as_view(), name='caregiver-detail'),
    path('my-profile/', MyCaregiverProfileView.as_view(), name='my-caregiver-profile'),
]
