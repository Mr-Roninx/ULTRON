import heapq
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class WorldEvent(BaseModel):
    event_id: str
    event_type: str
    entity_id: str
    timestamp: int
    visibility: str = "OBSERVABLE" # OBSERVABLE, HIDDEN, EVALUATOR_ONLY
    causal_parent_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    sequence_index: int = 0

    def __lt__(self, other: "WorldEvent") -> bool:
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.sequence_index < other.sequence_index

class PersistentEventPriorityQueue:
    """
    Chronological priority queue for deterministic temporal event execution.
    Maintains strict ordering by timestamp and insertion sequence index.
    """
    def __init__(self):
        self._heap: List[WorldEvent] = []
        self._counter: int = 0

    def push(self, event: WorldEvent):
        event.sequence_index = self._counter
        self._counter += 1
        heapq.heappush(self._heap, event)

    def pop(self) -> Optional[WorldEvent]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)

    def peek(self) -> Optional[WorldEvent]:
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
