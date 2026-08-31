import pytest
from synthetic_payment_universe.world_v13.behavior.liquidity import latent_civilization_liquidity_engine, LatentLiquidityProfile

def test_latent_liquidity_oracle_evaluation():
    p = LatentLiquidityProfile(customer_id="c_liq_test", salary_day=1, current_cash_reserve=50000.0)
    latent_civilization_liquidity_engine.register_profile(p)

    is_liq = latent_civilization_liquidity_engine.is_customer_liquid("c_liq_test", 1760000000)
    assert is_liq is True
