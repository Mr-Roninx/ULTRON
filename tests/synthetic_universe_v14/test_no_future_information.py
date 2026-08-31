import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world
from synthetic_payment_universe.world_v14.clock import emergent_clock

def test_no_future_information_in_builder(tmp_path):
    w = create_emergent_population_world(master_seed=606, profile_name="tiny", storage_dir=str(tmp_path))
    now = emergent_clock.now()
    slice_data = w.observation_builder.build_slice("c_v14_000000", "pmt_v14_000000_01", now)

    assert slice_data["current_time"] == now
    assert "true_root_cause" not in slice_data["payment"]
    assert "oracle_optimal_action" not in slice_data["payment"]
