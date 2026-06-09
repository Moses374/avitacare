from django.urls import path
from .views import MyFamilyProfileView

urlpatterns = [
    path('my-profile/', MyFamilyProfileView.as_view(), name='my-family-profile'),
]
