from django.urls import path
from .views import PendingVerificationsView, VerifyCaregiverView, AuditLogView

urlpatterns = [
    path('pending-verifications/', PendingVerificationsView.as_view(), name='pending-verifications'),
    path('verify-caregiver/<int:pk>/', VerifyCaregiverView.as_view(), name='verify-caregiver'),
    path('audit-logs/', AuditLogView.as_view(), name='audit-logs'),
]
