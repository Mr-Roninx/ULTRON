import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world
from synthetic_payment_universe.world_v14.events.micro_events import MicroEconomicEvent

def test_event_insert_idempotency(tmp_path):
    w = create_emergent_population_world(master_seed=909, profile_name="tiny", storage_dir=str(tmp_path))
    evt = MicroEconomicEvent(
        event_id="evt_idem_1",
        event_type="TEST_EVENT",
        entity_id="c_1",
        timestamp=1760000000
    )
    # Insert twice
    w.repository.insert_economic_events([evt])
    w.repository.insert_economic_events([evt])

    with w.repository.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM economic_events WHERE event_id = 'evt_idem_1'")
        assert c.fetchone()[0] == 1
