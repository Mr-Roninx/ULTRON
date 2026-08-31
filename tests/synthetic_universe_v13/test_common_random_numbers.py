import pytest
from synthetic_payment_universe.world_v13.counterfactual.common_random_numbers import CommonRandomNumberManager

def test_common_random_numbers_reproducibility():
    m1 = CommonRandomNumberManager(master_seed=777)
    m2 = CommonRandomNumberManager(master_seed=777)

    r1 = m1.get_branch_rng("dp_1", "RETRY").random()
    r2 = m2.get_branch_rng("dp_1", "RETRY").random()
    assert r1 == r2
