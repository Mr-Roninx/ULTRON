import pytest
from synthetic_payment_universe.world_v12.temporal.priority_queue import PersistentEventPriorityQueue, WorldEvent

def test_priority_queue_strict_ordering():
    pq = PersistentEventPriorityQueue()
    pq.push(WorldEvent(event_id="e_3", event_type="TEST", entity_id="1", timestamp=300))
    pq.push(WorldEvent(event_id="e_1", event_type="TEST", entity_id="1", timestamp=100))
    pq.push(WorldEvent(event_id="e_2", event_type="TEST", entity_id="1", timestamp=200))

    assert pq.pop().event_id == "e_1"
    assert pq.pop().event_id == "e_2"
    assert pq.pop().event_id == "e_3"
