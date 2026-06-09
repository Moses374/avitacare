from django.urls import path
from .views import ReviewListCreateView, CaregiverReviewsView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-list'),
    path('caregiver/<int:caregiver_id>/', CaregiverReviewsView.as_view(), name='caregiver-reviews'),
]
