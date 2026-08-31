from typing import List, Dict, Any, Callable, Optional
from synthetic_payment_universe.world_v13.events.event import EconomicEvent
from synthetic_payment_universe.world_v13.events.queue import PersistentCivilizationEventQueue
from synthetic_payment_universe.world_v13.repository import SQLiteCivilizationRepository

class CivilizationEventProcessor:
    """
    Processes chronological economic events and commits state changes to the persistent repository.
    """
    def __init__(self, repository: SQLiteCivilizationRepository):
        self.repository = repository
        self.queue = PersistentCivilizationEventQueue()
        self.handlers: Dict[str, List[Callable[[EconomicEvent], None]]] = {}

    def register_handler(self, event_type: str, handler: Callable[[EconomicEvent], None]):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def schedule_event(self, event: EconomicEvent):
        self.queue.push(event)

    def process_until(self, target_timestamp: int) -> List[EconomicEvent]:
        processed: List[EconomicEvent] = []
        batch_to_insert: List[EconomicEvent] = []

        while self.queue.has_events_up_to(target_timestamp):
            evt = self.queue.pop()
            if not evt:
                break

            # Dispatch handlers
            if evt.event_type in self.handlers:
                for h in self.handlers[evt.event_type]:
                    h(evt)

            processed.append(evt)
            batch_to_insert.append(evt)

            if len(batch_to_insert) >= 200:
                self.repository.insert_economic_events(batch_to_insert)
                batch_to_insert.clear()

        if batch_to_insert:
            self.repository.insert_economic_events(batch_to_insert)

        return processed
