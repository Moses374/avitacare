"""
Priority queue for urgent service requests.

Urgency levels map to integer priorities:
  high   → 1  (lowest number = highest priority)
  medium → 2
  low    → 3
"""

import heapq
from service_requests.models import ServiceRequest

PRIORITY_MAP = {
    ServiceRequest.UrgencyLevel.HIGH: 1,
    ServiceRequest.UrgencyLevel.MEDIUM: 2,
    ServiceRequest.UrgencyLevel.LOW: 3,
}


class RequestPriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # tiebreaker: earlier submissions first

    def push(self, request: ServiceRequest):
        priority = PRIORITY_MAP.get(request.urgency_level, 3)
        # Negate created_at so earlier timestamps sort first within same priority
        heapq.heappush(self._heap, (priority, self._counter, request.id))
        self._counter += 1

    def pop(self) -> int | None:
        """Return the next request ID by priority, or None if empty."""
        if self._heap:
            _, _, request_id = heapq.heappop(self._heap)
            return request_id
        return None

    def peek(self) -> int | None:
        if self._heap:
            return self._heap[0][2]
        return None

    def __len__(self):
        return len(self._heap)


def build_queue_from_db() -> RequestPriorityQueue:
    """Load all open requests into a fresh priority queue."""
    q = RequestPriorityQueue()
    open_requests = ServiceRequest.objects.filter(status='open').order_by('created_at')
    for req in open_requests:
        q.push(req)
    return q
