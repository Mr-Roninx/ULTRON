import pytest
from synthetic_payment_universe.world_v13.clock import economic_clock
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization
from synthetic_payment_universe.world_v13.observation.builder import ObservationSliceBuilder

def test_no_future_information_in_agent_slice(tmp_path):
    w = create_economic_civilization(master_seed=111, profile_name="tiny", storage_dir=str(tmp_path))
    builder = ObservationSliceBuilder(w.observation_api)

    now = economic_clock.now()
    slice_data = builder.build_opportunity_slice("c_civ_000000", "pmt_civ_000000_01")

    assert slice_data["current_time"] == now
    assert "true_root_cause" not in slice_data["payment"]
    assert "oracle_optimal_action" not in slice_data["payment"]
