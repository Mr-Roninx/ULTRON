import pytest
from synthetic_payment_universe.world_v12.behavior.liquidity_engine import latent_liquidity_engine
from synthetic_payment_universe.world_v12.observation.firewall import WorldObservationFirewall

def test_latent_liquidity_isolation():
    latent_liquidity_engine.reset()
    now = 1760000000

    latent_liquidity_engine.register_customer_liquidity(
        customer_id="c_iso_test",
        salary_day=1,
        inflow_amount=150000.0,
        next_inflow_timestamp=now + 86400
    )

    state = latent_liquidity_engine.get_latent_state("c_iso_test")
    assert state is not None

    # Firewall must completely strip latent fields
    sanitized = WorldObservationFirewall.sanitize({"customer_id": "c_iso_test", "created_at": now, "latent_salary_day": 1, "next_liquidity_window": now + 86400}, now)
    assert "latent_salary_day" not in sanitized
    assert "next_liquidity_window" not in sanitized
