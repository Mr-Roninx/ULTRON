import pytest
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer, Payment
from synthetic_payment_universe.observation.observation_builder import universe_observation_api

def test_observation_api_sanitization():
    universe_observation_api.reset()
    now = 1760000000
    clock.reset(now)

    cust = Customer(
        customer_id="c_obs_1",
        name="Observation Corp",
        latent_profile="PATIENT",
        latent_salary_day=1,
        created_at=now
    )
    pmt = Payment(
        payment_id="p_obs_1",
        customer_id=cust.customer_id,
        merchant_id="m_1",
        amount=24700.0,
        created_at=now
    )
    universe_observation_api.register_entities(customers=[cust], payments=[pmt])

    obs_c = universe_observation_api.observe_customer("c_obs_1", now)
    assert obs_c is not None
    assert "latent_profile" not in obs_c
    assert "latent_salary_day" not in obs_c

    obs_exp = universe_observation_api.observe_customer_exposure("c_obs_1", now)
    assert obs_exp["total_exposure"] == 24700.0
