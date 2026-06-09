from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from service_requests.models import ServiceRequest
from .matcher import match_caregivers


class MatchCaregiversView(APIView):
    """Return ranked caregivers for a given service request."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, request_id):
        try:
            service_request = ServiceRequest.objects.get(id=request_id, family=request.user)
        except ServiceRequest.DoesNotExist:
            return Response({'detail': 'Service request not found.'}, status=404)
        matches = match_caregivers(service_request)
        return Response({'matches': matches})
