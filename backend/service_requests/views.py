from rest_framework import generics, permissions
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


class ServiceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
