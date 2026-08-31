import heapq
from typing import List, Dict, Any, Optional, Tuple
from simulator.clock import clock
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.schema.visibility import EventVisibility, VisibilityGuard

class TemporalWorldEngine:
    """
    Priority-queue event-driven temporal world engine.
    Synchronized with VirtualClock, guarantees chronological causality and zero lookahead leakage.
    """
    def __init__(self):
        # Priority queue item: (timestamp, event_id, UnifiedTemporalEvent)
        self._event_queue: List[Tuple[int, str, UnifiedTemporalEvent]] = []
        self._event_history: List[UnifiedTemporalEvent] = []

    def schedule_event(self, event: UnifiedTemporalEvent):
        heapq.heappush(self._event_queue, (event.timestamp, event.event_id, event))

    def advance_to(self, target_timestamp: int) -> List[UnifiedTemporalEvent]:
        """Advances clock and processes all events up to target_timestamp in strict temporal order."""
        processed: List[UnifiedTemporalEvent] = []
        while self._event_queue and self._event_queue[0][0] <= target_timestamp:
            ts, eid, evt = heapq.heappop(self._event_queue)
            clock.advance_to(ts)
            self._event_history.append(evt)
            processed.append(evt)
        clock.advance_to(target_timestamp)
        return processed

    def get_events_until(
        self,
        current_time: int,
        visibility: Optional[EventVisibility] = EventVisibility.OBSERVABLE
    ) -> List[UnifiedTemporalEvent]:
        """Returns past and current events satisfying temporal boundary and visibility filter."""
        results: List[UnifiedTemporalEvent] = []
        for evt in self._event_history:
            if evt.timestamp <= current_time:
                if visibility is None or evt.visibility == visibility:
                    results.append(evt)
        return results

    def reset(self):
        self._event_queue.clear()
        self._event_history.clear()

temporal_world_engine = TemporalWorldEngine()
