from django.urls import path
from .views import MatchCaregiversView

urlpatterns = [
    path('request/<int:request_id>/', MatchCaregiversView.as_view(), name='match-caregivers'),
]
