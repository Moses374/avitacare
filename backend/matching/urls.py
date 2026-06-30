from django.urls import path
from .views import MatchCaregiversView, RequestQueueView

urlpatterns = [
    path('request/<int:request_id>/', MatchCaregiversView.as_view(), name='match-caregivers'),
    path('queue/', RequestQueueView.as_view(), name='request-queue'),
]
