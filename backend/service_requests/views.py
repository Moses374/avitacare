from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'family':
            return ServiceRequest.objects.filter(family=user)
        return ServiceRequest.objects.filter(status='open')

    def perform_create(self, serializer):
        if self.request.user.role != 'family':
            raise PermissionDenied('Only families can submit service requests.')
        serializer.save()


class ServiceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
