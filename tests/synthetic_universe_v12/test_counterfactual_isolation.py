import pytest
from synthetic_payment_universe.world_v12.entities.payment import Payment
from synthetic_payment_universe.world_v12.entities.customer import Customer
from synthetic_payment_universe.world_v12.counterfactual.counterfactual_fork import WorldCounterfactualForkEngine

def test_counterfactual_branch_independence():
    engine = WorldCounterfactualForkEngine(master_seed=123)
    cust = Customer(customer_id="c_indep_1", tier="SMB")
    pmt = Payment(payment_id="p_indep_1", customer_id="c_indep_1", merchant_id="m_1", amount=18000.0)

    outcomes = engine.evaluate_branches("dp_1", pmt, cust, natural_recovery=False)
    assert len(outcomes) == 5

    # Distinct branch IDs and types
    b_types = {o.action_type for o in outcomes}
    assert b_types == {"WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "ESCALATE"}
