import pytest
from synthetic_payment_universe.world_v12.entities.payment import Payment
from synthetic_payment_universe.world_v12.entities.customer import Customer
from synthetic_payment_universe.world_v12.counterfactual.counterfactual_fork import WorldCounterfactualForkEngine

def test_natural_recovery_in_counterfactual_evaluation():
    engine = WorldCounterfactualForkEngine(master_seed=42)
    cust = Customer(customer_id="c_nat_1", tier="SMB")
    pmt = Payment(payment_id="p_nat_1", customer_id="c_nat_1", merchant_id="m_1", amount=24700.0, failure_code="91")

    # With natural recovery = True, WAIT branch succeeds
    outcomes = engine.evaluate_branches("dp_nat_1", pmt, cust, natural_recovery=True)
    wait_b = next(o for o in outcomes if o.action_type == "WAIT")
    assert wait_b.success is True
    assert wait_b.recovered_amount == 24700.0
    assert wait_b.net_economic_value == 24700.0

    # With natural recovery = False, WAIT branch fails
    outcomes_no = engine.evaluate_branches("dp_nat_2", pmt, cust, natural_recovery=False)
    wait_no = next(o for o in outcomes_no if o.action_type == "WAIT")
    assert wait_no.success is False
    assert wait_no.net_economic_value == 0.0
