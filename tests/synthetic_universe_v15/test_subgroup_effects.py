import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_subgroup_sensitivity_distribution(tmp_path):
    w = create_adversarial_world(master_seed=999, profile_name="tiny", storage_dir=str(tmp_path))
    sensitivities = {c.sensitivity_type.value for c in w.customers.values()}
    assert "HIGHLY_SENSITIVE" in sensitivities
    assert "NATURAL_RECOVERER" in sensitivities
