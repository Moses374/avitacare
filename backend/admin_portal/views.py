from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from caregivers.models import CaregiverProfile
from .models import AuditLog
from .serializers import AuditLogSerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.ADMIN


class PendingVerificationsView(generics.ListAPIView):
    """List caregivers awaiting verification."""
    permission_classes = [IsAdmin]

    def get(self, request):
        from caregivers.serializers import CaregiverProfileSerializer
        pending = CaregiverProfile.objects.filter(verification_status='pending')
        return Response(CaregiverProfileSerializer(pending, many=True).data)


class VerifyCaregiverView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        action = request.data.get('action')  # 'approve' or 'reject'
        try:
            profile = CaregiverProfile.objects.get(pk=pk)
        except CaregiverProfile.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        if action == 'approve':
            profile.verification_status = 'verified'
            log_action = 'Approved caregiver'
        elif action == 'reject':
            profile.verification_status = 'rejected'
            log_action = 'Rejected caregiver'
        else:
            return Response({'detail': 'Invalid action. Use approve or reject.'}, status=400)

        profile.save()
        AuditLog.objects.create(admin=request.user, action=log_action, target_user=profile.user)
        return Response({'status': profile.verification_status})


class AuditLogView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
