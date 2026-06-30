from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from accounts.permissions import IsAdmin
from service_requests.models import ServiceRequest
from service_requests.serializers import ServiceRequestSerializer

from .matcher import match_caregivers
from .priority_queue import build_queue_from_db


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


class RequestQueueView(APIView):
    """Return open service requests ordered by the urgency priority queue.

    Surfaces the most time-sensitive requests (e.g. post-hospital discharge)
    first, so admins can triage which requests need attention.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        queue = build_queue_from_db()
        ordered_ids = []
        while len(queue):
            ordered_ids.append(queue.pop())

        requests_by_id = ServiceRequest.objects.filter(id__in=ordered_ids).in_bulk()
        ordered_requests = [requests_by_id[rid] for rid in ordered_ids if rid in requests_by_id]
        serializer = ServiceRequestSerializer(ordered_requests, many=True)
        return Response({'queue': serializer.data})
