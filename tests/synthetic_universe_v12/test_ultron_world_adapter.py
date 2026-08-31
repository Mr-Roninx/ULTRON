import pytest
from simulator.clock import clock
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.generator.world_generator import WorldDataPopulator
from synthetic_payment_universe.world_v12.observation.adapter import WorldAdapter

def test_ultron_world_adapter_observation(tmp_path):
    w = create_world(master_seed=123, profile=WorldProfile.TINY, storage_dir=str(tmp_path))
    pop = WorldDataPopulator(w)
    pop.populate()

    adapter = WorldAdapter(w)
    cust_obs = adapter.observe_customer("c_w12_000000")
    assert cust_obs is not None
    assert "latent_profile" not in cust_obs

    gw_obs = adapter.observe_gateway("GATEWAY_A")
    assert gw_obs["health_score"] > 0.80
