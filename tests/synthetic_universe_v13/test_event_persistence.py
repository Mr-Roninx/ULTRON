import pytest
from synthetic_payment_universe.world_v13.events.event import EconomicEvent
from synthetic_payment_universe.world_v13.events.queue import PersistentCivilizationEventQueue

def test_event_queue_chronological_ordering():
    q = PersistentCivilizationEventQueue()
    q.push(EconomicEvent(event_id="e_3", event_type="TEST", entity_id="1", timestamp=300))
    q.push(EconomicEvent(event_id="e_1", event_type="TEST", entity_id="1", timestamp=100))
    q.push(EconomicEvent(event_id="e_2", event_type="TEST", entity_id="1", timestamp=200))

    assert q.pop().event_id == "e_1"
    assert q.pop().event_id == "e_2"
    assert q.pop().event_id == "e_3"
