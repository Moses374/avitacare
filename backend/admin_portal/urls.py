from django.urls import path

from .views import (
    AuditLogView,
    DeactivateAccountView,
    PendingVerificationsView,
    ReactivateAccountView,
    ReportsView,
    UsersListView,
    VerifyCaregiverView,
)

urlpatterns = [
    path('pending-verifications/', PendingVerificationsView.as_view(), name='pending-verifications'),
    path('verify-caregiver/<int:pk>/', VerifyCaregiverView.as_view(), name='verify-caregiver'),
    path('deactivate-account/<int:pk>/', DeactivateAccountView.as_view(), name='deactivate-account'),
    path('reactivate-account/<int:pk>/', ReactivateAccountView.as_view(), name='reactivate-account'),
    path('users/', UsersListView.as_view(), name='admin-users'),
    path('audit-logs/', AuditLogView.as_view(), name='audit-logs'),
    path('reports/', ReportsView.as_view(), name='reports'),
]
