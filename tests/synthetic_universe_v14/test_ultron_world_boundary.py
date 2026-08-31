import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_ultron_world_boundary_execution(tmp_path):
    w = create_emergent_population_world(master_seed=12, profile_name="tiny", storage_dir=str(tmp_path))
    success, res = w.execute_agent_action("c_v14_000000", "pmt_v14_000000_01", "SWITCH_GATEWAY")
    assert success is True
    assert res["status"] == "EXECUTED"

    # Gateway load updated as side effect
    assert w.gateway_engine.gateways["GATEWAY_B"].active_load > 0
