from typing import Dict, Any, List, Callable
from simulator.clock import clock

class SimulationEventBus:
    """
    Decoupled event bus managing asynchronous state transitions, domain events,
    and webhook subscriptions across the sandbox simulator.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._history: List[Dict[str, Any]] = []

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": clock.now()
        }
        self._history.append(event)
        for handler in self._subscribers.get(event_type, []):
            handler(event)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def reset(self):
        self._subscribers.clear()
        self._history.clear()

simulation_event_bus = SimulationEventBus()
