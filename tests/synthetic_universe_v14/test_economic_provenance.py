import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world
from synthetic_payment_universe.world_v14.ledger.provenance_tracker import provenance_tracker

def test_recovery_provenance_trace(tmp_path):
    w = create_emergent_population_world(master_seed=333, profile_name="tiny", storage_dir=str(tmp_path))
    w.record_recovery("pmt_v14_000001_01", "c_v14_000001", "m_v14_0001", 35000.0, "SWITCH_GATEWAY")

    exp = provenance_tracker.explain("pmt_v14_000001_01")
    assert exp is not None
    assert exp["recovered_amount"] == 35000.0
    assert exp["action_type"] == "SWITCH_GATEWAY"
