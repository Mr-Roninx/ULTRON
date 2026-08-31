import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_population_level_action_side_effects(tmp_path):
    w = create_adversarial_world(master_seed=123, profile_name="tiny", storage_dir=str(tmp_path))
    # Execute gateway switch action
    ok, res = w.execute_agent_action("c_v15_000000", "pmt_v15_000000_01", "SWITCH_GATEWAY")
    assert ok is True
    assert w.gateway_externalities.gateways["GATEWAY_B"].current_load > 0
