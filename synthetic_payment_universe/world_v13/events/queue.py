import heapq
from typing import List, Optional
from synthetic_payment_universe.world_v13.events.event import EconomicEvent

class PersistentCivilizationEventQueue:
    """
    Chronological event queue maintaining strict deterministic ordering by (timestamp, sequence_index).
    """
    def __init__(self):
        self._heap: List[EconomicEvent] = []
        self._counter: int = 0

    def push(self, event: EconomicEvent):
        event.sequence_index = self._counter
        self._counter += 1
        heapq.heappush(self._heap, event)

    def pop(self) -> Optional[EconomicEvent]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def peek(self) -> Optional[EconomicEvent]:
        if not self._heap:
            return None
        return self._heap[0]

    def has_events_up_to(self, target_timestamp: int) -> bool:
        return bool(self._heap and self._heap[0].timestamp <= target_timestamp)

    def size(self) -> int:
        return len(self._heap)

    def clear(self):
        self._heap.clear()
        self._counter = 0
