from typing import List, Dict, Callable
import uuid
from simulator.clock import clock
from simulator.events import DomainEvent

class EventBus:
    def __init__(self):
        self.events: List[DomainEvent] = []
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def reset(self):
        self.events = []
        self.subscribers = {}
        
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def publish(self, event: DomainEvent):
        # Allow caller to provide partial event and we fill in ID/timestamp if needed?
        # Better: caller provides fully formed DomainEvent.
        self.events.append(event)
        
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                handler(event)
                
    def get_history(self) -> List[DomainEvent]:
        return self.events

event_bus = EventBus()
