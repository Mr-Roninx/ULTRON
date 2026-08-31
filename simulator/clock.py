import heapq
from typing import Callable, Tuple, Any, List, Optional
from backend.simulation.temporal_events import SimulationEvent
import uuid

class VirtualClock:
    def __init__(self):
        self.current_time = 0
        # Priority queue for scheduled events: (time, event_id, event_obj)
        self.events: List[Tuple[int, str, Any]] = []
        self._next_event_id = 0
        self.cancelled_events = set()
        
    def reset(self, start_time: int = 0):
        self.current_time = start_time
        self.events = []
        self._next_event_id = 0
        self.cancelled_events = set()
        
    def now(self) -> int:
        return self.current_time
        
    def get_time(self) -> int:
        return self.current_time
        
    def advance(self, seconds: int) -> int:
        if seconds < 0:
            raise ValueError("Cannot advance clock backwards")
        target_time = self.current_time + seconds
        self.advance_to(target_time)
        return self.current_time

    def advance_to(self, timestamp: int) -> int:
        if timestamp < self.current_time:
            raise ValueError("Cannot advance clock backwards")
        self.run_until(timestamp)
        return self.current_time

    def advance_next(self) -> int:
        if not self.has_pending_events():
            return self.current_time
        event = self.peek_next()
        if event:
            self.advance_to(event.scheduled_at)
        return self.current_time

    def schedule(self, at_time: int, event_or_callback: Any) -> str:
        if at_time < self.current_time:
            raise ValueError(f"Cannot schedule event in the past (now: {self.current_time}, target: {at_time})")
        
        if callable(event_or_callback):
            event = SimulationEvent(
                event_type="GENERIC_CALLBACK",
                scheduled_at=at_time,
                execution_callback=event_or_callback
            )
        else:
            event = event_or_callback
            event.scheduled_at = at_time

        event_id = event.event_id if hasattr(event, "event_id") else f"evt_{self._next_event_id}"
        self._next_event_id += 1
        heapq.heappush(self.events, (at_time, event_id, event))
        return event_id
        
    def cancel(self, event_id: str) -> bool:
        self.cancelled_events.add(event_id)
        return True
        
    def peek_next(self) -> Optional[Any]:
        while self.events:
            at_time, event_id, event_obj = self.events[0]
            if event_id in self.cancelled_events:
                heapq.heappop(self.events)
                continue
            return event_obj
        return None

    def pop_next(self) -> Optional[Any]:
        while self.events:
            at_time, event_id, event_obj = self.events[0]
            if event_id in self.cancelled_events:
                heapq.heappop(self.events)
                continue
            heapq.heappop(self.events)
            self.current_time = max(self.current_time, at_time)
            return event_obj
        return None

    def has_pending_events(self) -> bool:
        return self.peek_next() is not None

    def next_event(self) -> Tuple[int, Callable] | None:
        """Legacy compatibility method for older tests."""
        evt = self.peek_next()
        if evt and hasattr(evt, "execution_callback") and evt.execution_callback:
            return (evt.scheduled_at, evt.execution_callback)
        # If it's a newer event without an explicit callback, we might need a no-op to fulfill legacy API expectations,
        # but normally tests expect the callback they passed.
        if evt:
             # Just return a dummy callable so legacy code can pop it
             return (evt.scheduled_at, lambda: None)
        return None
        
    def run_until(self, target_time: int) -> None:
        while True:
            evt = self.peek_next()
            if not evt:
                break
            
            if evt.scheduled_at > target_time:
                break
                
            # Pop and execute
            evt = self.pop_next()
            self.current_time = evt.scheduled_at
            
            if hasattr(evt, "execution_callback") and evt.execution_callback:
                evt.execution_callback()
            
        self.current_time = max(self.current_time, target_time)

clock = VirtualClock()
