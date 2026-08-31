import heapq
from typing import List, Optional
from synthetic_payment_universe.world_v14.events.micro_events import MicroEconomicEvent

class PopulationEventQueue:
    """
    Priority queue ordered by (timestamp, sequence_index) ensuring deterministic event dispatch.
    """
    def __init__(self):
        self._heap: List[MicroEconomicEvent] = []
        self._counter: int = 0

    def push(self, event: MicroEconomicEvent):
        event.sequence_index = self._counter
        self._counter += 1
        heapq.heappush(self._heap, event)

    def pop(self) -> Optional[MicroEconomicEvent]:
        return heapq.heappop(self._heap) if self._heap else None

    def has_events_up_to(self, target_timestamp: int) -> bool:
        return bool(self._heap and self._heap[0].timestamp <= target_timestamp)

    def size(self) -> int:
        return len(self._heap)
