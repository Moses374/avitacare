from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from bookings.models import Booking
from caregivers.models import CaregiverProfile
from caregivers.serializers import CaregiverProfileSerializer
from notifications.models import Notification
from notifications.views import notify
from reviews.models import Review
from service_requests.models import ServiceRequest

from .models import AuditLog
from .serializers import AdminUserSerializer, AuditLogSerializer

User = get_user_model()


class PendingVerificationsView(generics.ListAPIView):
    """List caregivers awaiting verification."""
    serializer_class = CaregiverProfileSerializer
    permission_classes = [IsAdmin]
    queryset = CaregiverProfile.objects.filter(
        verification_status=CaregiverProfile.VerificationStatus.PENDING
    )


class VerifyCaregiverView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        action = request.data.get('action')  # 'approve' or 'reject'
        try:
            profile = CaregiverProfile.objects.get(pk=pk)
        except CaregiverProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if action == 'approve':
            profile.verification_status = CaregiverProfile.VerificationStatus.VERIFIED
            log_action = 'Approved caregiver'
        elif action == 'reject':
            profile.verification_status = CaregiverProfile.VerificationStatus.REJECTED
            log_action = 'Rejected caregiver'
        else:
            return Response({'detail': 'Invalid action. Use approve or reject.'}, status=400)

        profile.save(update_fields=['verification_status', 'updated_at'])
        AuditLog.objects.create(admin=request.user, action=log_action, target_user=profile)
        notify(profile, Notification.Category.VERIFICATION, f'Your profile was {profile.verification_status}.')
        return Response({'status': profile.verification_status})


class DeactivateAccountView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        user.is_active = False
        user.save(update_fields=['is_active'])
        AuditLog.objects.create(
            admin=request.user, action='Deactivated account', target_user=user
        )
        return Response({'detail': 'Account deactivated.'})


class ReactivateAccountView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)
        user.is_active = True
        user.save(update_fields=['is_active'])
        AuditLog.objects.create(
            admin=request.user, action='Reactivated account', target_user=user
        )
        return Response({'detail': 'Account reactivated.'})


class UsersListView(generics.ListAPIView):
    """Browse all platform users for admin monitoring and account management."""
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        role = self.request.query_params.get('role', '').strip()
        search = self.request.query_params.get('search', '').strip()
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(email__icontains=search)
        return qs


class AuditLogView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]


class ReportsView(APIView):
    """Aggregate platform metrics for the admin dashboard."""
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'users': {
                'total': User.objects.count(),
                'families': User.objects.filter(role='family').count(),
                'caregivers': User.objects.filter(role='caregiver').count(),
                'active': User.objects.filter(is_active=True).count(),
            },
            'caregivers': {
                'pending_verification': CaregiverProfile.objects.filter(
                    verification_status=CaregiverProfile.VerificationStatus.PENDING
                ).count(),
                'verified': CaregiverProfile.objects.filter(
                    verification_status=CaregiverProfile.VerificationStatus.VERIFIED
                ).count(),
                'rejected': CaregiverProfile.objects.filter(
                    verification_status=CaregiverProfile.VerificationStatus.REJECTED
                ).count(),
            },
            'service_requests': {
                'open': ServiceRequest.objects.filter(status='open').count(),
                'matched': ServiceRequest.objects.filter(status='matched').count(),
                'closed': ServiceRequest.objects.filter(status='closed').count(),
            },
            'bookings': {
                'pending': Booking.objects.filter(status=Booking.Status.PENDING).count(),
                'confirmed': Booking.objects.filter(status=Booking.Status.CONFIRMED).count(),
                'ongoing': Booking.objects.filter(status=Booking.Status.ONGOING).count(),
                'completed': Booking.objects.filter(status=Booking.Status.COMPLETED).count(),
                'cancelled': Booking.objects.filter(status=Booking.Status.CANCELLED).count(),
            },
            'reviews': {
                'total': Review.objects.count(),
                'average_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
            },
        })
