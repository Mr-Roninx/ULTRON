import pytest
from simulator.clock import clock
from synthetic_payment_universe.schema.events import UnifiedTemporalEvent
from synthetic_payment_universe.world.temporal_engine import temporal_world_engine

def test_temporal_engine_event_queue():
    temporal_world_engine.reset()
    clock.reset(1760000000)

    e1 = UnifiedTemporalEvent(event_id="e_1", event_type="PMT_FAIL", entity_id="p_1", timestamp=1760000100)
    e2 = UnifiedTemporalEvent(event_id="e_2", event_type="CHAOS", entity_id="gw_1", timestamp=1760007200)
    e3 = UnifiedTemporalEvent(event_id="e_3", event_type="RETRY", entity_id="p_1", timestamp=1760000050)

    # Schedule out-of-order
    temporal_world_engine.schedule_event(e1)
    temporal_world_engine.schedule_event(e2)
    temporal_world_engine.schedule_event(e3)

    # Advance clock to 1760000150
    processed = temporal_world_engine.advance_to(1760000150)
    assert len(processed) == 2
    # Check that events processed in strict ascending timestamp order
    assert processed[0].event_id == "e_3"
    assert processed[1].event_id == "e_1"
    assert clock.now() == 1760000150
