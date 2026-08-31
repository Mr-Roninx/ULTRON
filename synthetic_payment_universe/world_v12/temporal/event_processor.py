from typing import List, Dict, Any, Callable, Optional
from synthetic_payment_universe.world_v12.temporal.priority_queue import PersistentEventPriorityQueue, WorldEvent
from synthetic_payment_universe.world_v12.state.repository import SQLiteWorldRepository

class TemporalEventProcessor:
    """
    Step-by-step chronological event processor.
    Advances simulation time, dispatches events to registered domain handlers, and writes event logs.
    """
    def __init__(self, repository: SQLiteWorldRepository):
        self.repo = repository
        self.queue = PersistentEventPriorityQueue()
        self.handlers: Dict[str, List[Callable[[WorldEvent], None]]] = {}

    def register_handler(self, event_type: str, handler: Callable[[WorldEvent], None]):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def schedule_event(self, event: WorldEvent):
        self.queue.push(event)

    def process_until(self, target_timestamp: int) -> List[WorldEvent]:
        processed: List[WorldEvent] = []
        while self.queue.has_events_up_to(target_timestamp):
            evt = self.queue.pop()
            if not evt:
                break
            # Dispatch to domain handlers
            if evt.event_type in self.handlers:
                for h in self.handlers[evt.event_type]:
                    h(evt)
            # Universal handlers
            if "*" in self.handlers:
                for h in self.handlers["*"]:
                    h(evt)
            processed.append(evt)

        # Batch persist processed events to SQLite repository
        if processed:
            self.repo.insert_events_chunk(processed)

        return processed
